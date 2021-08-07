from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='Cart'),
    path('add_cart/<int:product_id>', views.add_cart, name='AddToCart'),
    path('decrement_cart_item/<int:product_id>/<int:cart_item_id>', views.decrement_cart_item, name='DecrementCartItem'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>', views.remove_cart_item, name='RemoveCartItem'),

    # Checkout
    path('checkout/', views.checkout, name='Checkout'),
]