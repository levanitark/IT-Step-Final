from django.urls import path

from . import views

urlpatterns = [
    path("", views.menu, name="menu"),
    path("basket/", views.basket, name="basket"),
    path("basket/add/<int:product_id>/", views.add_to_basket, name="add_to_basket"),
    path("basket/<int:item_id>/", views.update_basket, name="update_basket"),
    path("checkout/", views.checkout, name="checkout"),
]
