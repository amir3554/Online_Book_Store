from django.contrib import admin
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractWeek
from django.db.models import Sum
from .models import OrderReport
from oprations.models import Order
import json

@admin.register(OrderReport)
class OrderReportAdmin(admin.ModelAdmin):
    
    change_list_template = 'admin/records/orders.html'

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
    
    def changelist_view(self, request, extra_context=None):
        
        yearly_stats = (
            Order.objects.select_related('transaction')
            .annotate(year=ExtractYear('created_at'))
            .values('year')
            .annotate(sum=Sum(('transaction__amount'))))

        monthly_stats = (
            Order.objects.select_related('transaction')
            .annotate(year=ExtractYear('created_at'))
            .annotate(month=ExtractMonth('created_at'))
            .values('year','month')
            .annotate(sum=Sum(('transaction__amount'))))[:30]

        weekly_stats = (
            Order.objects.select_related('transaction')
            .annotate(year=ExtractYear('created_at'))
            .annotate(week=ExtractWeek('created_at'))
            .values('year','week')
            .annotate(sum=Sum(('transaction__amount'))))[:30]

        context = {
            **self.admin_site.each_context(request),
            'yearly_stats' : json.dumps(list(yearly_stats), default=str),
            'monthly_stats' : json.dumps(list(monthly_stats), default=str),
            'weekly_stats' : json.dumps(list(weekly_stats), default=str),
            'title' : "Order Records"
        }

        return TemplateResponse(
            request, self.change_list_template, context
        )
