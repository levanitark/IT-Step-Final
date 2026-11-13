import requests

from . import api


def basket_count(request):
    # count for the header
    try:
        items = api.get_basket()
    except requests.RequestException:
        return {"basket_count": 0}
    return {"basket_count": sum(item["quantity"] for item in items)}
