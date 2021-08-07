from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.

# Private method to return session_id
def _get_cart_id(request):
    session_id = request.session.session_key  # getting the sessionid from cookies
        
    if not session_id:
        session_id = request.session.create()  # if session doesn't exist, create one
    return session_id  # return the session


# Add to cart/Increment cart item
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)            # Getting the product whose id is provided
    product_variations = []

    user = request.user

    ################################
    # If the user is authenticated
    if user.is_authenticated:
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    
                    product_variations.append(variation)
                    
                except:
                    pass

        is_cart_item_exist = CartItem.objects.filter(product=product, user=user).exists()

        # If the cart item is already there
        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(product=product, user=user) # Get the cart item

            existing_variations_list = []
            item_id_list = []
            # Getting existing variations in cart
            for item in cart_item:
                existing_variations = item.variations.all()
                existing_variations_list.append(list(existing_variations))
                item_id_list.append(item.id)

            # If selected variations are already there in cart item
            if product_variations in existing_variations_list:
                index = existing_variations_list.index(product_variations)
                item_id = item_id_list[index]
                item = CartItem.objects.get(product=product, user=user, id=item_id)
                item.quantity += 1
                item.save()
            
            # if the selected variation is not in the cart item
            else:
                new_cart_item = CartItem.objects.create(product=product, user=user, quantity=1)
                if len(product_variations) > 0:
                    new_cart_item.variations.clear()
                    new_cart_item.variations.add(*product_variations)
                new_cart_item.save()                                             # save cart item
        
        # If the cart item is not there
        else:                                 # create cart item if doesn't exist
            cart_item = CartItem.objects.create(                        
                product=product,
                user=user,
                quantity=1,
            )

            if len(product_variations) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)

            cart_item.save()                                            # Save the cart item
        return redirect('Cart')
   
    ################################
    # If the user is not authenticated
    else:
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    
                    product_variations.append(variation)
                    
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_get_cart_id(request)) # Getting the cart item
        except Cart.DoesNotExist:                                  # If cart doesn't exist, create one
            cart = Cart.objects.create(
                cart_id=_get_cart_id(request),
            )
            cart.save()                                            # Save the cart

        is_cart_item_exist = CartItem.objects.filter(product=product, cart=cart).exists()

        # If the cart item is already there
        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(product=product, cart=cart) # Get the cart item

            existing_variations_list = []
            item_id_list = []
            # Getting existing variations in cart
            for item in cart_item:
                existing_variations = item.variations.all()
                existing_variations_list.append(list(existing_variations))
                item_id_list.append(item.id)

            # If selected variations are already there in cart item
            if product_variations in existing_variations_list:
                index = existing_variations_list.index(product_variations)
                item_id = item_id_list[index]
                item = CartItem.objects.get(product=product, cart=cart, id=item_id)
                item.quantity += 1
                item.save()
            
            # if the selected variation is not in the cart item
            else:
                new_cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
                if len(product_variations) > 0:
                    new_cart_item.variations.clear()
                    new_cart_item.variations.add(*product_variations)
                new_cart_item.save()                                             # save cart item
        
        # If the cart item is not there
        else:                                 # create cart item if doesn't exist
            cart_item = CartItem.objects.create(                        
                product=product,
                cart=cart,
                quantity=1,
            )

            if len(product_variations) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)

            cart_item.save()                                            # Save the cart item
        return redirect('Cart')


# decrementing cart item
def decrement_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('Cart')


# Removing cart item 
def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    
    return redirect('Cart')


# cart_items display
def cart(request, total=0, quantity=0, tax=0, grand_total=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total)/100                   # Calculating 2% tax
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request=request, template_name='store/cart.html', context=context)

# Checkout
@login_required(login_url='Login')
def checkout(request, total=0, quantity=0, tax=0, grand_total=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total)/100                   # Calculating 2% tax
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request=request, template_name='store/checkout.html', context=context)