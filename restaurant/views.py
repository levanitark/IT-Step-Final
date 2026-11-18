from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import BasketItem, Category, Order, OrderItem, Product


def menu(request):
    category = request.GET.get("category", "")
    min_spiciness = request.GET.get("min_spiciness", "0")
    max_spiciness = request.GET.get("max_spiciness", "4")

    products = Product.objects.all()
    if category.isdigit():
        products = products.filter(category_id=category)
    if min_spiciness.isdigit():
        products = products.filter(spiciness__gte=min_spiciness)
    if max_spiciness.isdigit():
        products = products.filter(spiciness__lte=max_spiciness)
    if request.GET.get("no_nuts"):
        products = products.filter(nuts=False)
    if request.GET.get("vegetarian"):
        products = products.filter(vegetarian=True)

    return render(request, "restaurant/menu.html", {
        "categories": Category.objects.all(),
        "products": products,
        # (0, "Not spicy"), (1, "🌶️"), (2, "🌶️🌶️") ...
        "spiciness_levels": [(i, "🌶️" * i or "Not spicy") for i in range(5)],
        "category": category,
        "min_spiciness": min_spiciness,
        "max_spiciness": max_spiciness,
    })


@require_POST
def add_to_basket(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = BasketItem.objects.get_or_create(product=product)
    if not created:
        item.quantity += 1
        item.save()
    return redirect(request.META.get("HTTP_REFERER", "menu"))


def basket(request):
    items = BasketItem.objects.select_related("product")
    total = sum(item.subtotal() for item in items)
    return render(request, "restaurant/basket.html", {"items": items, "total": total})


@require_POST
def update_basket(request, item_id):
    item = get_object_or_404(BasketItem, id=item_id)
    action = request.POST.get("action")
    if action == "plus":
        item.quantity += 1
    elif action == "minus":
        item.quantity -= 1

    if action == "remove" or item.quantity < 1:
        item.delete()
    else:
        item.save()
    return redirect("basket")


@require_POST
@transaction.atomic
def checkout(request):
    items = BasketItem.objects.select_related("product")
    if not items:
        return redirect("basket")

    total = sum(item.subtotal() for item in items)
    order = Order.objects.create(total=total)
    for item in items:
        OrderItem.objects.create(
            order=order, product=item.product, price=item.product.price, quantity=item.quantity
        )
    items.delete()

    messages.success(request, f"Thank you! Order #{order.id} was placed. Total: ${total}")
    return redirect("basket")
