from django.contrib import admin
from .models import Payment, Order, OrderProduct

class OrderProductInlineAdmin(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ['order', 'user', 'payment', 'product', 'quantity', 'product_price', 'ordered']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'email', 'phone', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'email', 'phone']
    list_per_page = 10
    inlines = [OrderProductInlineAdmin]

# Register your models here.
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)