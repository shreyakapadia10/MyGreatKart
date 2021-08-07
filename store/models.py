from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    images = models.ImageField(upload_to='photos/products')
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def average_review(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])

        return avg

    def review_counter(self):
        review_count = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('rating'))
        
        count = 0

        if review_count['count'] is not None:
            count = int(review_count['count'])
        return count

    def get_url(self):
        return reverse('ProductDetails', args=[self.category.slug, self.slug])

    def __str__(self) -> str:
        return f'{self.name} ({self.category.name})'

VARIATION_CATEGORY_CHOICES = (
    ('Color', 'Color'),
    ('Size', 'Size'),
)

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='Color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='Size', is_active=True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=50, choices=VARIATION_CATEGORY_CHOICES)
    variation_value = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    def __str__(self):
        return f'{self.variation_value}'


class ReviewRating(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.subject} ({self.rating} stars)'


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='shop/product_images', max_length=255)

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'

    def __str__(self):
        return f'{self.product.name}'