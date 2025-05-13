from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from mystore_project import settings
from .forms import UserInfoForm, MyPayPalPaymentsForm
from store.models import Product, Cart
from .models import Transaction, PaymentMethod, TransactionStatus, Order, OrderProduct
from django.core.mail import send_mail, get_connection
from django.template.loader import render_to_string
from django.utils.translation import gettext as trans
import math
import stripe
from stripe.error import SignatureVerificationError #type: ignore
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.views.decorators.csrf import csrf_exempt



def make_transaction(request, pm):

    form = UserInfoForm(request.POST)   
    if form.is_valid():
        cart = Cart.objects.filter(session=request.session.session_key).last()
        products = Product.objects.filter(pk__in=cart.items) #type:ignore
        total = 0   

        for product in products:
            total += product.price

        if total <= 0:
            return None
        
        return Transaction.objects.create(
            customer=form.cleaned_data,
            session=request.session.session_key,
            payment_method=pm,
            items = cart.items, #type:ignore
            amount= math.ceil(total),
            )


def make_order(transaction_id):
    transaction = Transaction.objects.get(pk=transaction_id)
    transaction.status = TransactionStatus.COMPLETED
    transaction.save()
    order = Order.objects.create(transaction=transaction)
    order.transaction = transaction
    order.save()
    products = Product.objects.filter(pk__in=transaction.items)
    for product in products:
        OrderProduct.objects.create(order=order, product=product, price=product.price)

    msg_html = render_to_string('emails/order.html',
                                {
                                    'order':order,
                                    'products':products,
                                }
                            )
    connection = get_connection()
    send_mail(
        subject='New Order',
        html_message=msg_html,
        message=msg_html,
        from_email='noreply@example.com',
        recipient_list=[order.transaction.customer_email], #type:ignore
        connection=connection,
        )
    connection.close()


def check_out(request):
    return render(
        request, 'check_out.html'
    )


def check_out_complete(request):
    Cart.objects.filter(session=request.session.session_key).delete()
    return render(
        request, 'check_out_complete.html'
    )




'''
                                  /////
                ////
    /////////  ////////  //////// /////  ////////////      ////////
  ///////////  ////////  //////// /////  /////////////   ////// /////
  //////       ////      ////     /////  ////     ///// /////     ////
    /////////  ////      ////     /////  ////      //// //////////////
         ///// ////      ////     /////  ////     /////  ////
  ///////////  ////////  ////     /////  /////////////    ///////////
   ////////      //////  ////     /////  //// //////        ///////
                                         ////
                                         ////
'''


def stripe_transaction(request):
    transaction = make_transaction(request, PaymentMethod.STRIPE)
    if not transaction:
        return JsonResponse(
            {'message': trans('Please inter a valid info.')}
            , status=400
        )
    
    stripe.api_key = settings.STRIPE_SECRET_KEY

    intent = stripe.PaymentIntent.create(
        amount=transaction.amount * 100,# this is the stripe format # type: ignore
        currency=settings.CURRENCY,
        payment_method_types=['card'],
        metadata={
            'transaction': transaction.pk
        }
    )
    return JsonResponse(
        {
            'client_secret': intent["client_secret"]
        }
    )


@csrf_exempt
def stripe_webhook(request):
    payload = request.body # to get to the data of the request
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_ENDPOINT_SECRET
        )

    except ValueError:
        print('Invalid payload')
        return HttpResponse(status=400)
        
    except SignatureVerificationError:
        print('Invalid signature')
        return HttpResponse(status=400)
    
    try:
        print("🔔 Event type received:", event.type)
        # Handle the event
        if event.type == 'payment_intent.succeeded':
            print("📥 Event: payment_intent.succeeded RECEIVED")
            payment_intent = event.data.object
            print("✅ Payment succeeded with ID:", payment_intent.id) #type:ignore
            transaction_id = payment_intent.metadata.transaction #type:ignore
            make_order(transaction_id)

        elif event.type == 'charge.succeeded':
            charge = event.data.object
            print("💰 Charge succeeded:", charge.id) #type:ignore

        else:
            print('Unhandled event type {}'.format(event.type))
        
    except Exception as e:
        import traceback
        print("❌ Exception in webhook:", e)
        traceback.print_exc()
        return HttpResponse(status=500)

    return HttpResponse(status=200)
        

def stripe_config(request):
    return JsonResponse(
        {
            'public_key': settings.STRIPE_PUBLISHABLE_KEY,
        }
    )





'''
////////////////////////////////////////////////////////////////////////
///             /////////////////////////            ///////////////////
///     /////    ////////////////////////     /////    /////////////////
///    ///  ///   ///////////////////////    ///  ///   ////////////////
///     /////    ////////////////////////     /////    /////////////////
///             /////////////////////////             //////////////////
///   ///////////////////////////////////   ////////////////////////////
///   ///////////////////////////////////   ////////////////////////////
///   ///////////////////////////////////   ////////////////////////////
///   ///////////////////////////////////   ////////////////////////////
////////////////////////////////////////////////////////////////////////
'''

def paypal_transaction(request):
    transaction = make_transaction(request, PaymentMethod.PAYPAL)
    if not transaction:
        return JsonResponse({'message':trans('Please enter a valid information.')},status=400)

    form = MyPayPalPaymentsForm(initial={
        'business': settings.PAYPAL_EMAIL,
        'amount': transaction.amount,
        'invoice': transaction.pk,
        'currency_code': settings.CURRENCY,
        'return_url': f'http://{request.get_host()}{reverse('CheckoutComplete')}',
        'cancel_url': f'http://{request.get_host()}{reverse('StoreCheckout')}'
    })

    return HttpResponse(form.render())

@csrf_exempt
def paypal_webhook(sender, **kwargs):
    if sender.payment_status == ST_PP_COMPLETED:
        if sender.reciever_email != settings.PAYPAL_EMAIL:
            return
        print('Payment intent was successful')
        make_order(sender.invoice)

valid_ipn_received.connect(paypal_webhook)


