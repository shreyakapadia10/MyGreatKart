from django.contrib import admin
from store.models import Product, ProductGallery, ReviewRating, Variation
import admin_thumbnails
# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInlineAdmin(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'date_created', 'date_modified', 'is_available']

    prepopulated_fields = {'slug': ('name',)}

    inlines = [ProductGalleryInlineAdmin]

class VariationAdmin(admin.ModelAdmin):
    list_display = ['product', 'variation_category', 'variation_value', 'is_active']
    list_editable = ('is_active',)
    list_filter =  ['product', 'variation_category', 'variation_value']

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)