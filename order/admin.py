from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.utils.translation import gettext as _
from .models import Product, Order, OrderItem, QRCode


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    def get_order_status(self, obj):
        return obj.order_status

    get_order_status.short_description = 'Order Status'
    get_order_status.admin_order_field = 'order_status'
    get_order_status.empty_value_display = '-'

    def get_address_type(self, obj):
        return obj.get_address_type_display()  # Use get_<field_name>_display() to get the human-readable value of a choice field.

    get_address_type.short_description = 'Address Type'
    get_address_type.admin_order_field = 'address_type'
    get_address_type.empty_value_display = '-'

    list_display = (
        'user_name', 'mobile_number', 'product', 'quantity', 'get_order_status', 'order_date', 'get_address_type',
        'order_time', 'payment_method')
    list_filter = (('order_date', DateFieldListFilter), 'payment_method', 'order_status', 'address_type')
    date_hierarchy = 'order_date'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'order_date':
            kwargs['widget'] = admin.widgets.AdminDateWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.order_status = 'ordered'  # Set initial order status as "ordered"
        obj.save()


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    pass
