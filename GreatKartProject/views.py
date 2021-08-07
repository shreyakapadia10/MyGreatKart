from store.models import Product, ReviewRating
from django.shortcuts import render

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('date_created')[:8]

    # Get product reviews 
    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product__id=product.id, status=True)

    context = {
        'products': products, 
        'reviews': reviews,
    }
    return render(request=request, template_name='index.html', context=context)