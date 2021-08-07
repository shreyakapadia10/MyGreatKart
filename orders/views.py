from store.models import Product
from django.shortcuts import render, redirect
from django.http import JsonResponse
from cart.models import CartItem
from .forms import OrderForm
from .models import Order, OrderProduct, Payment
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import datetime
import json

def payment(request):
    if request.method == 'POST':
        user = request.user
        # Get the response from JS 
        response = json.loads(request.body)
        order = Order.objects.get(user=user, order_number=response['order_number'], is_ordered=False)

        # Save the payment details
        payment = Payment(
            user = user,
            payment_id = response['payment_id'],
            payment_method = response['payment_method'],
            amount_paid = order.order_total,
            status = response['status'],
        )
        payment.save()

        # Update payment details in Order Table
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to OrderProduct Table
        cart_items = CartItem.objects.filter(user=user)

        for item in cart_items:
            order_product = OrderProduct(
                order = order,
                payment = payment,
                user = user,
                product = item.product,
                quantity = item.quantity,
                product_price = item.product.price,
                ordered = True,
            )
            order_product.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variations = cart_item.variations.all()
            order_product = OrderProduct.objects.get(id=order_product.id)
            order_product.variations.set(product_variations)
            order_product.save()

            # Reduce quantity of sold products
            product = Product.objects.get(id=cart_item.product.id)
            product.stock -= cart_item.quantity
            product.save()
        
        # Clear Cart
        CartItem.objects.filter(user=user, is_active=True).delete()

        # Send confirmation mail to user
        mail_subject = 'Thank you for ordering with us!'
        message = render_to_string('orders/order_confirmation_email.html', {
            'user': user,
            'order_number': order.order_number,
        })

        to_email = user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        # Send order number and transaction id back to sendData method using JsonResponse
        json_response = {
            'order_id': order.order_number,
            'payment_id': payment.payment_id,
        }
        return JsonResponse(json_response)

    return render(request, 'orders/payment.html')

# Create your views here.
def place_order(request, total = 0, quantity=0):
    if request.user.is_authenticated:
        user = request.user

        cart_items = CartItem.objects.filter(user=user, is_active=True)
        cart_items_count = cart_items.count()
        grand_total = 0
        tax = 0

        # If cart is empty i.e. the cart items count is less than or equal to 0
        if cart_items_count <= 0:
            return redirect('Store')
        
        else:
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity

            tax = (2 * total)/100                   # Calculating 2% tax
            grand_total = total + tax

            if request.method == 'POST':
                form = OrderForm(request.POST)
                if form.is_valid():
                    order_data = Order()

                    # Getting form data
                    order_data.user = user
                    order_data.first_name = form.cleaned_data.get('first_name')
                    order_data.last_name = form.cleaned_data.get('last_name')
                    order_data.phone = form.cleaned_data.get('phone')
                    order_data.email = form.cleaned_data.get('email')
                    order_data.address_line_1 = form.cleaned_data.get('address_line_1')
                    order_data.address_line_2 = form.cleaned_data.get('address_line_2')
                    order_data.country = form.cleaned_data.get('country')
                    order_data.state = form.cleaned_data.get('state')
                    order_data.city = form.cleaned_data.get('city')
                    order_data.order_note = form.cleaned_data.get('order_note')
                    order_data.order_total = grand_total
                    order_data.tax = tax
                    order_data.ip = request.META.get('REMOTE_ADDR')
                    order_data.save()

                    # Generating order_number

                    year = int(datetime.date.today().strftime('%Y'))
                    month = int(datetime.date.today().strftime('%m'))
                    today_date = int(datetime.date.today().strftime('%d'))
                
                    date = datetime.date(year, month, today_date)
                    current_date = date.strftime("%Y%m%d")

                    order_number = current_date + str(order_data.id)
                    order_data.order_number = order_number
                    order_data.save()

                    order = Order.objects.get(user=user, order_number=order_number, is_ordered=False)
                    context = {
                        'order': order,
                        'cart_items': cart_items,
                        'tax': tax,
                        'total': total,
                        'grand_total': grand_total,
                    }
                    return render(request, 'orders/payment.html', context)
                else:
                    return redirect('Checkout')
            else:
                return redirect('Checkout')

    else:
        return redirect('Login')


def order_complete(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    user = request.user
    try:
        total = 0

        order = Order.objects.get(order_number=order_id, user=user, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id, user=user, ordered=True)
        payment = Payment.objects.get(payment_id=payment_id, user=user)
        
        for cart_item in ordered_products:
                total += (cart_item.product.price * cart_item.quantity)
                
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'user': user,
            'payment': payment,
            'total': total,
        }
        return render(request, 'orders/order_complete.html', context)
        
    except (Order.DoesNotExist, OrderProduct.DoesNotExist, Payment.DoesNotExist):
        return redirect('Home')