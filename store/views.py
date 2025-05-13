from django.shortcuts import render, redirect
from .models import Product, Slider, Category, Cart
from django.core.paginator import Paginator
from django.db.models import Q
from django.http.response import JsonResponse
from django.contrib.sessions.models import Session



def index(request):
    products = Product.objects.filter(featured=True)
    slides = Slider.objects.all().order_by('order')

    return render(
        request, 'index.html',
        {
            'products' : products,
            'slides' : slides
        }
    )



def product(request, pid):
    product = Product.objects.get(id=pid)
    return render(
        request, 'product.html',
        {
            'product' : product
        }
    )




def category(request, category=None):
    query = request.GET.get('query', '').strip()
    if category is None:
        category = request.GET.get('category', None)
    
    filters = Q()
    
    if query:
        filters &= Q(name__icontains=query) | Q(description__icontains=query)

    # استخدام إما category أو cid
    category_filter = category
    if category_filter:
        filters &= Q(category_id=category_filter)

    products = Product.objects.filter(filters)

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'category.html', {
        'page_obj': page_obj,
        'category': category_filter,
        'query': query
    })






def cart(request):
    return render(
        request, 'cart.html'
    )

def cart_update(request, pid=None):

    if not request.session.session_key:
        request.session.create()# if there is not a session yet, create one
    # there are multible entry
    session_id = request.session.session_key# get the session id
    session = Session.objects.get(session_key=session_id)
    cart_model = Cart.objects.filter(session=session).last()# get the last cart with that session_id
    
    if cart_model is None: # maybe there is a cart but its still empty *dict*.'
        cart_model = Cart.objects.create(session=session, items=[pid])

    elif pid not in cart_model.items:
        cart_model.items.append(pid)
        cart_model.save()
        
        return JsonResponse(
        {
            'message': 'Item added to cart',
            'items_count': len(cart_model.items),
        }
    )

    elif pid in cart_model.items:
        return JsonResponse(
            { 
                'message' : 'the product is already in the cart' ,
                'items_count': len(cart_model.items),
            }
        )

    return JsonResponse(
        {
            'message': 'error ocurred while trying to add to cart.',
        }
    )



def cart_remove(request, pid=None):
    session_id = request.session.session_key

    if not session_id:
        return JsonResponse({ 'message' : 'there is no session id' })
    
    cart_model = Cart.objects.filter(session=session_id).last()

    if cart_model is None:
        return JsonResponse({ 'message' : 'there is no cart' })
    
    elif pid in cart_model.items:
        cart_model.items.remove(pid)
        cart_model.save()

    else:
        return JsonResponse({ 'message' : 'the product not in the cart, or other err, try again.' })
    
    return JsonResponse(
        {
            'message': 'Item removed from the cart',
            'items_count': len(cart_model.items),
        }
    )


