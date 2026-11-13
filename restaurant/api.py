# api docs: https://restaurant.stepprojects.ge/swagger/index.html
import requests

API_URL = "https://restaurant.stepprojects.ge/api"
TIMEOUT = 10


def get_categories():
    response = requests.get(f"{API_URL}/Categories/GetAll", timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_products(category_id=None, no_nuts=False, vegetarian=False):
    params = {}
    if category_id is not None:
        params["categoryId"] = category_id
    if no_nuts:
        params["nuts"] = "false"
    if vegetarian:
        params["vegeterian"] = "true"  # api spells it like this

    response = requests.get(f"{API_URL}/Products/GetFiltered", params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_product(product_id):
    response = requests.get(f"{API_URL}/Products/GetAll", timeout=TIMEOUT)
    response.raise_for_status()
    for product in response.json():
        if product["id"] == product_id:
            return product
    return None


def get_basket():
    response = requests.get(f"{API_URL}/Baskets/GetAll", timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def add_to_basket(product_id, quantity, price):
    data = {"productId": product_id, "quantity": quantity, "price": price}
    response = requests.post(f"{API_URL}/Baskets/AddToBasket", json=data, timeout=TIMEOUT)
    response.raise_for_status()


def update_basket(product_id, quantity, price):
    data = {"productId": product_id, "quantity": quantity, "price": price}
    response = requests.put(f"{API_URL}/Baskets/UpdateBasket", json=data, timeout=TIMEOUT)
    response.raise_for_status()


def remove_from_basket(product_id):
    response = requests.delete(f"{API_URL}/Baskets/DeleteProduct/{product_id}", timeout=TIMEOUT)
    response.raise_for_status()
