from decimal import Decimal

import requests
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from . import api
from .models import Order, OrderItem

API_ERROR = "Could not connect to the restaurant server. Please try again later."


def to_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def menu(request):
    selected_category = to_int(request.GET.get("category"))
    min_spiciness = to_int(request.GET.get("min_spiciness"), 0)
    max_spiciness = to_int(request.GET.get("max_spiciness"), 4)
    no_nuts = request.GET.get("no_nuts") == "on"
    vegetarian = request.GET.get("vegetarian") == "on"

    context = {
        "categories": [],
        "products": [],
        "selected_category": selected_category,
        "min_spiciness": min_spiciness,
        "max_spiciness": max_spiciness,
        "no_nuts": no_nuts,
        "vegetarian": vegetarian,
        "spiciness_levels": range(0, 5),
        "all_url": "?" + query_with_category(request, None),
        "error": None,
    }

    try:
        categories = api.get_categories()
        products = api.get_products(selected_category, no_nuts, vegetarian)
    except requests.RequestException:
        context["error"] = API_ERROR
        return render(request, "restaurant/menu.html", context)

    # keep filters when changing category
    for category in categories:
        category["url"] = "?" + query_with_category(request, category["id"])
    context["categories"] = categories

    if min_spiciness > max_spiciness:
        context["error"] = "Min spiciness can't be higher than max spiciness."
    else:
        # api has no min/max so we filter here
        context["products"] = [
            p for p in products if min_spiciness <= p["spiciness"] <= max_spiciness
        ]

    return render(request, "restaurant/menu.html", context)


def query_with_category(request, category_id):
    params = request.GET.copy()
    if category_id is None:
        params.pop("category", None)
    else:
        params["category"] = category_id
    return params.urlencode()


@require_POST
def add_to_basket(request):
    product_id = to_int(request.POST.get("product_id"))

    try:
        product = api.get_product(product_id)
        if product is None:
            messages.error(request, "That dish does not exist.")
        else:
            # if already in basket add 1
            existing = find_in_basket(api.get_basket(), product_id)
            if existing:
                api.update_basket(product_id, existing["quantity"] + 1, product["price"])
            else:
                api.add_to_basket(product_id, 1, product["price"])
            messages.success(request, f"{product['name']} added to basket.")
    except requests.RequestException:
        messages.error(request, API_ERROR)

    # go back to menu
    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("menu")


def basket(request):
    try:
        items = api.get_basket()
    except requests.RequestException:
        return render(request, "restaurant/basket.html", {"items": [], "total": 0, "error": API_ERROR})

    total = 0
    for item in items:
        item["subtotal"] = item["product"]["price"] * item["quantity"]
        total += item["subtotal"]

    return render(request, "restaurant/basket.html", {"items": items, "total": total, "error": None})


@require_POST
def change_quantity(request):
    product_id = to_int(request.POST.get("product_id"))
    change = 1 if request.POST.get("action") == "plus" else -1

    try:
        item = find_in_basket(api.get_basket(), product_id)
        if item:
            new_quantity = item["quantity"] + change
            if new_quantity < 1:
                api.remove_from_basket(product_id)
            else:
                api.update_basket(product_id, new_quantity, item["product"]["price"])
    except requests.RequestException:
        messages.error(request, API_ERROR)

    return redirect("basket")


@require_POST
def remove_from_basket(request):
    product_id = to_int(request.POST.get("product_id"))

    try:
        api.remove_from_basket(product_id)
    except requests.RequestException:
        messages.error(request, API_ERROR)

    return redirect("basket")


@require_POST
def place_order(request):
    try:
        items = api.get_basket()
    except requests.RequestException:
        messages.error(request, API_ERROR)
        return redirect("basket")

    if not items:
        messages.error(request, "Your basket is empty.")
        return redirect("basket")

    # merge same dishes
    dishes = {}
    for item in items:
        product = item["product"]
        if product["id"] in dishes:
            dishes[product["id"]]["quantity"] += item["quantity"]
        else:
            dishes[product["id"]] = {
                "name": product["name"],
                "price": Decimal(str(product["price"])),
                "quantity": item["quantity"],
            }

    # save order
    with transaction.atomic():
        order = Order.objects.create(total=0)
        total = Decimal("0")
        for product_id, dish in dishes.items():
            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                name=dish["name"],
                price=dish["price"],
                quantity=dish["quantity"],
            )
            total += dish["price"] * dish["quantity"]
        order.total = total
        order.save()

    # clear basket
    try:
        for item in items:
            api.remove_from_basket(item["product"]["id"])
    except requests.RequestException:
        messages.error(request, "Your order was saved, but the basket could not be emptied.")

    messages.success(request, f"Thank you! Order #{order.id} was placed. Total: ${total:.2f}")
    return redirect("basket")


def find_in_basket(items, product_id):
    for item in items:
        if item["product"]["id"] == product_id:
            return item
    return None
