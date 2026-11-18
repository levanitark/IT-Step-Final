from django.db.models import Sum

from .models import BasketItem


def basket_count(request):
    if not request.user.is_authenticated:
        return {"basket_count": 0}
    count = BasketItem.objects.filter(user=request.user).aggregate(total=Sum("quantity"))["total"]
    return {"basket_count": count or 0}
