from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='Store'),
    path('category/<slug:category_slug>/', views.store, name='ProductsByCategory'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_details, name='ProductDetails'),
    path('search/', views.search, name='Search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='SubmitReview'),
]