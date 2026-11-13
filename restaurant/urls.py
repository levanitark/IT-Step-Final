from django.urls import path

from . import views

urlpatterns = [
    path("", views.menu, name="menu"),
    path("basket/", views.basket, name="basket"),
    path("basket/add/", views.add_to_basket, name="add_to_basket"),
    path("basket/change/", views.change_quantity, name="change_quantity"),
    path("basket/remove/", views.remove_from_basket, name="remove_from_basket"),
    path("basket/order/", views.place_order, name="place_order"),
]
