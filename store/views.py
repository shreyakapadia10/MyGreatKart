from accounts.models import UserProfile
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, ProductGallery, ReviewRating
from category.models import Category
from cart.models import CartItem
from cart.views import _get_cart_id
from django.core.paginator import Paginator
from .forms import ReviewRatingForm
from django.contrib import messages
from orders.models import OrderProduct

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('-date_created')
        paginator = Paginator(products, 3)

    else:
        products = Product.objects.all().filter(is_available=True).order_by('-date_created')
        paginator = Paginator(products, 6)
        
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count
    }
    return render(request=request, template_name='store/store.html', context=context)


def product_details(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_get_cart_id(request), product=product).exists()
    except Product.DoesNotExist as e:
        raise e

    if request.user.is_authenticated:
        try:
            is_ordered = OrderProduct.objects.filter(user=request.user, product__id=product.id).exists()
        except OrderProduct.DoesNotExist:
            is_ordered = None
    else:
        is_ordered = None
        
    # Get product reviews 
    reviews = ReviewRating.objects.all().filter(product__id=product.id, status=True).order_by('-updated_at')
    
    # Get product gallery
    product_gallery = ProductGallery.objects.filter(product=product)

    # # Get the profiles
    # for review in reviews:
    #     profiles = UserProfile.objects.filter(user=review.user)
    #     print(profiles)

    context = {
        'product': product,
        'in_cart': in_cart,
        'is_ordered': is_ordered,
        'reviews': reviews,
        'product_gallery': product_gallery,
        # 'profiles': profiles,
    }
    return render(request=request, template_name='store/product_details.html', context=context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')

        if keyword:
            products = Product.objects.order_by('-date_created').filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
            
            product_count = products.count()
            context = {
                'products': products,
                'product_count': product_count
            }
            return render(request=request, template_name='store/store.html', context=context)
        else:
            context = { 
                'product_count': 0,
            }
            return render(request=request, template_name='store/store.html', context=context)


def submit_review(request, product_id):
    if request.method == 'POST':
        user = request.user
        url = request.META.get('HTTP_REFERER')
        
        # If the review already exists, update it
        try:
            review = ReviewRating.objects.get(user__id=user.id, product__id=product_id)
            form = ReviewRatingForm(request.POST, instance=review)
            form.save()
            messages.success(request, 'Thank You! Your review has been successfully updated!')

        # If the review does not exist, create it
        except ReviewRating.DoesNotExist:
            form = ReviewRatingForm(request.POST)
            if form.is_valid():
                review_data = ReviewRating()
                review_data.user = user
                review_data.product_id = product_id
                review_data.rating = form.cleaned_data.get('rating')
                review_data.subject = form.cleaned_data.get('subject')
                review_data.review = form.cleaned_data.get('review')
                review_data.ip = request.META.get('REMOTE_ADDR')
                review_data.save()
                messages.success(request, 'Thank You! Your review has been successfully submitted!')
        return redirect(url)