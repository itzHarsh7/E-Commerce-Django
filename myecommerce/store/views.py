from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Cart
from .forms import ProductForm, CategoryForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from django.contrib import messages
from django.db.models import Sum, F
from django.http import JsonResponse

def contact(request):
    return render(request, 'contact.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('/')
    return render(request, 'signin.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # group = Group.objects.get(name='Author')
            # user.groups.add(group)
            messages.success(request, "Account has been created")
            return redirect('signin')
    form = SignUpForm()
    return render(request, 'signup.html',{'form':form})

def signout(request):
    logout(request)
    return redirect('/')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, 'category_detail.html', {'category': category})

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'category_confirm_delete.html', {'category': category})


@login_required
def cart_detail(request):
    user_cart = Cart.objects.filter(user=request.user).first()
    total_price = user_cart.products.aggregate(total=Sum('price'))['total'] if user_cart else 0
    return render(request, 'cart_detail.html', {'cart': user_cart, 'total_price': total_price})

@login_required
def add_to_cart(request,pk):
    product = get_object_or_404(Product, pk=pk)
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    user_cart.products.add(product)
    product.quantity = F('quantity') - 1
    product.save()
    
    user_cart.products.add(product)
    return redirect('/')

@login_required
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    user_cart = Cart.objects.get(user=request.user)
    user_cart.products.remove(product)
    product.quantity = F('quantity') + 1
    product.save()
    return redirect('cart_detail')

@login_required
def clear_cart(request):
    user_cart = Cart.objects.get(user=request.user)
    for product in user_cart.products.all():
        product.quantity = F('quantity') + 1
        product.save()
    user_cart.products.clear()
    return redirect('cart_detail')