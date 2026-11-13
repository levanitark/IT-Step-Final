from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ["name", "price", "quantity", "subtotal"]
    readonly_fields = ["name", "price", "quantity", "subtotal"]
    can_delete = False

    # items come from the basket
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["__str__", "created_at", "total", "status"]
    list_editable = ["status"]
    list_filter = ["status", "created_at"]
    readonly_fields = ["created_at", "total"]
    inlines = [OrderItemInline]

    # orders are made from the site
    def has_add_permission(self, request):
        return False
