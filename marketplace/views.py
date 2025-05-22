from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ProductForm
from .models import Product, Farm, Profile, ProductCategory, Order, OrderItem, Review
from django.core.mail import send_mail
import json

def home(request):
    featured_products = Product.objects.filter(stock__gt=0).order_by('-date_added')[:8]
    farms = Farm.objects.all()[:4]
    
    context = {
        'featured_products': featured_products,
        'farms': farms,
        'title': 'Home'
    }
    return render(request, 'marketplace/home.html', context)

def about(request):
    return render(request, 'marketplace/about.html', {'title': 'About Us'})

def contact(request):
    return render(request, 'marketplace/contact.html', {'title': 'Contact Us'})

# def contact(request):
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             # Process form and send email
#             send_mail(
#                 'Contact Form Submission',
#                 form.cleaned_data['message'],
#                 form.cleaned_data['email'],
#                 ['your@email.com'],
#             )
#             return redirect('contact_success')
#     else:
#         form = ContactForm()
#     return render(request, 'marketplace/contact.html', {'form': form})

def privacy(request):
    return render(request, 'marketplace/privacy.html', {'title': 'Privacy Policy'})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'marketplace/auth/register.html', {'form': form})

def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else []
    
    context = {
        'products': products,
        'query': query,
        'title': f'Search: {query}'
    }
    return render(request, 'marketplace/search.html', context)

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'marketplace/auth/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'marketplace/auth/profile.html', context)

@login_required
def farmer_dashboard(request):
    if not hasattr(request.user, 'farm'):
        return redirect('home')
    
    farm = request.user.farm
    products = Product.objects.filter(farm=farm)
    orders = Order.objects.filter(orderitem__product__farm=farm).distinct()
    
    # Add product form
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farm = farm
            product.save()
            return redirect('farmer_dashboard')
    else:
        form = ProductForm()
    
    context = {
        'farm': farm,
        'products': products,
        'orders': orders,
        'form': form,
        'title': 'Farmer Dashboard'
    }
    return render(request, 'marketplace/farmer/dashboard.html', context)

@transaction.atomic
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'marketplace/auth/register.html', {'form': form})

def shop(request):
    products = Product.objects.filter(stock__gt=0).order_by('-date_added')
    categories = ProductCategory.objects.all()
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category__id=category_id)
    
    # Filter by search query
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'title': 'Shop'
    }
    return render(request, 'marketplace/shop.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
    reviews = product.review_set.all()
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'title': product.name
    }
    return render(request, 'marketplace/product_detail.html', context)

def farm_detail(request, pk):
    farm = get_object_or_404(Farm, pk=pk)
    products = Product.objects.filter(farm=farm, stock__gt=0)
    
    context = {
        'farm': farm,
        'products': products,
        'title': farm.name
    }
    return render(request, 'marketplace/farm_detail.html', context)

def farm_list(request):
    farms = Farm.objects.all()
    
    context = {
        'farms': farms,
        'title': 'Our Farms'
    }
    return render(request, 'marketplace/farm_list.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    
    context = {
        'items': items,
        'order': order,
        'title': 'Shopping Cart'
    }
    return render(request, 'marketplace/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    
    context = {
        'items': items,
        'order': order,
        'title': 'Checkout'
    }
    return render(request, 'marketplace/checkout.html', context)

def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    
    customer = request.user
    product = Product.objects.get(id=productId)
    
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse('Item was added', safe=False)