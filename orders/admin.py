from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'full_name', 'total_amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method']
    inlines = [OrderItemInline]