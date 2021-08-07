from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='Dashboard'),
    path('dashboard/', views.dashboard, name='Dashboard'),
    path('register/', views.register, name='Register'),
    path('login/', views.login, name='Login'),
    path('logout/', views.logout, name='Logout'),
    
    path('forgot-password/', views.forgotPassword, name='ForgotPassword'),
    path('activate/<uidb64>/<token>/', views.activate, name='ActivateAccount'),
    path('reset-password-validate/<uidb64>/<token>/', views.resetPasswordValidate, name='ResetPasswordValidate'),
    path('reset-password/', views.resetPassword, name='ResetPassword'),

    path('my-orders/', views.my_orders, name='MyOrders'),
    path('update-profile/', views.update_profile, name='UpdateProfile'),
    path('change-password/', views.change_password, name='ChangePassword'),
    path('order-details/<int:order_number>/', views.order_details, name='OrderDetails'),
]