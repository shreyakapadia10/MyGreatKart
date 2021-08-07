from .models import Cart, CartItem
from .views import _get_cart_id

def get_cart_count(request):
    cart_count = 0

    if 'admin' in request.path:
        return {}
    else:
        try:
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)    
            else:
                cart = Cart.objects.get(cart_id=_get_cart_id(request))
                cart_items = CartItem.objects.all().filter(cart=cart)

            for cart_item in cart_items:
                cart_count += cart_item.quantity

        except Cart.DoesNotExist:
            pass
    return dict(cart_count=cart_count)