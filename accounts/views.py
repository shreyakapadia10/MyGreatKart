from orders.models import Order, OrderProduct
from django.http.response import HttpResponse
from accounts.forms import RegistrationForm, UserForm, UserProfileForm
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .models import Account, UserProfile

# Email Verification imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from cart.models import Cart, CartItem
from cart.views import _get_cart_id
import requests

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')
            password= form.cleaned_data.get('password')
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password, username=username)
            user.phone_number = phone_number
            user.save()

            # Create Profile Picture
            profile = UserProfile()
            profile.user = user
            profile.profile_picture = 'default/user_avatar.png'
            profile.save()

            # Email Verification Process
            current_site = get_current_site(request)
            mail_subject = 'Activate Your Account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            return redirect(f'/accounts/login/?command=verification&email={email}')
        else:
            messages.error(request, form.errors)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request=request, template_name='accounts/register.html', context=context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(request=request, email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_get_cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exist:
                    cart_items = CartItem.objects.filter(cart=cart)

                    # Getting available product variations by cart id
                    product_variations = []

                    for item in cart_items:
                        variations = item.variations.all()
                        product_variations.append(list(variations))

                    # Getting the variations of products which has been added by user
                    cart_items = CartItem.objects.filter(user=user) # Get the cart item
                    existing_variations_list = []
                    item_id_list = []

                    # Getting existing variations in cart

                    for item in cart_items:
                        existing_variations = item.variations.all()
                        existing_variations_list.append(list(existing_variations))
                        item_id_list.append(item.id)

                    # If selected variations are already there in cart item
                    for product_variation in product_variations:
                        if product_variation in existing_variations_list:
                            index = existing_variations_list.index(product_variation)
                            item_id = item_id_list[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_items = CartItem.objects.filter(cart=cart) # Get the cart item
                            for item in cart_items:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are logged in now!')

            url = request.META.get('HTTP_REFERER')
            
            try:
                query = requests.utils.urlparse(url).query # getting next=/cart/checkout
                # Making dictionary for next_url
                params = dict(x.split('=') for x in query.split('&'))

                if 'next' in params:
                    next_url = params['next']
                    return redirect(next_url)

            except:
                return redirect('Dashboard')
        else:
            messages.error(request, 'Please check the credentials again!')
            return redirect('Login')

    return render(request=request, template_name='accounts/login.html')


@login_required(login_url='Login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out now!')
    return redirect('Login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, Account.DoesNotExistError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully! You can login now!')
        return redirect('Login')
    else:
        messages.error(request, 'Activation Link Expired!')
        return redirect('Login')


@login_required(login_url='Login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user=request.user, is_ordered=True)
    order_count = orders.count()
    profile = UserProfile.objects.get(user=request.user)

    context = {
        'order_count': order_count,
        'profile': profile,
    }

    return render(request=request, template_name='accounts/dashboard.html', context=context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)
            
            # Reset Password Mail
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request=request, message='Password Reset Link Has Been Sent Successfully! Click on the link to reset your password!')

            return redirect('Login')
        else:
            messages.error(request=request, message='Account does not exists!')
            return redirect('ForgotPassword')
    
    return render(request, 'accounts/forgot-password.html')

def resetPasswordValidate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, Account.DoesNotExistError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please Reset Your Password!')
        return redirect('ResetPassword')
    else:
        messages.error(request, 'This Link Has Been Expired!')
        return redirect('Login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Your password has been changed successfully! You can Login Now!')
            return redirect('Login')
        else:
            messages.error(request, "Password don't match!")
            return redirect('ResetPassword')

    return render(request, 'accounts/reset-password.html')

@login_required(login_url='Login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }

    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='Login')
def update_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('UpdateProfile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
    }    
    return render(request, 'accounts/update_profile.html', context)


@login_required(login_url='Login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = Account.objects.get(username__exact=request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)

            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password Updated Successfully!')
                return redirect('ChangePassword')
            else:
                messages.error(request, 'Invalid Current Password!')
                return redirect('ChangePassword')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('ChangePassword')

    return render(request, 'accounts/change-password.html')


@login_required(login_url='Login')
def order_details(request, order_number):
    ordered_products = OrderProduct.objects.filter(order__order_number=order_number)
    order = Order.objects.get(order_number=order_number)
    total = 0

    for item in ordered_products:
        total += item.product_price * item.quantity

    context = {
        'ordered_products': ordered_products,
        'order': order,
        'total': total,
    }
    return render(request, 'accounts/order_details.html', context)