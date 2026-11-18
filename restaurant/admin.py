from django.contrib import admin

from .models import BasketItem, Category, Order, OrderItem, Product

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(BasketItem)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "created_at", "total"]
    inlines = [OrderItemInline]
