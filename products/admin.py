
from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock')
    search_fields = ('name',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    max_num = 0
    can_delete = False

    readonly_fields = (
        'product',
        'product_name',
        'quantity',
        'unit_price',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'full_name',
        'total_amount',
        'status',
        'created_at',
    )

    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'user__username', 'phone')

    readonly_fields = (
        'user',
        'full_name',
        'phone',
        'shipping_address',
        'total_amount',
        'created_at',
    )

    inlines = [OrderItemInline]

    def has_add_permission(self, request):
        return False
