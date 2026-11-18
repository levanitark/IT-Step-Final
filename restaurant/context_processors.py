from django.db.models import Sum

from .models import BasketItem


def basket_count(request):
    count = BasketItem.objects.aggregate(total=Sum("quantity"))["total"]
    return {"basket_count": count or 0}
