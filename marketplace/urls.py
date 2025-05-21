from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('farm/<int:pk>/', views.farm_detail, name='farm_detail'),
    path('farms/', views.farm_list, name='farms'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.update_item, name='update_item'),
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
]