
from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
]

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    path('cart/', views.view_cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('register/', views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='products/login.html'
        ),
        name='login'
    ),
    path('account/', views.account, name='account'),
    path('logout/', views.logout_view, name='logout'),
]

path('checkout/', views.checkout, name='checkout'),
path('orders/success/<int:order_id>/', views.order_success, name='order_success'),
path('orders/', views.order_history, name='order_history'),

path('checkout/', views.checkout, name='checkout'),
path(
    'orders/success/<int:order_id>/',
    views.order_success,
    name='order_success'
),
path('orders/', views.order_history, name='order_history'),
path(
    'orders/<int:order_id>/',
    views.order_detail,
    name='order_detail'
),