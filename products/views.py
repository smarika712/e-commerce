from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.decorators import admin_required
from .models import Product, Category
from .forms import ProductForm


def _get_cart_count(request):
    """Helper function to calculate total items in the cart."""
    cart = request.session.get('cart', {})
    return sum(
        item['quantity'] if isinstance(item, dict) else item
        for item in cart.values()
    )


def wishlist_add(request, product_id):
    """Toggles a product inside the session-based wishlist."""
    wishlist = request.session.get('wishlist', [])

    if product_id in wishlist:
        wishlist.remove(product_id)
        messages.info(request, 'Removed from wishlist.')
    else:
        wishlist.append(product_id)
        messages.success(request, 'Added to wishlist!')

    request.session['wishlist'] = wishlist
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


# ---------- Product Views ----------

def product_list(request, category_slug=None):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'products/list.html', {
        'products': products,
        'categories': categories,
        'category': category,
        'cart_count': _get_cart_count(request),
    })


def product_search(request):
    query = request.GET.get('q', '').strip()

    if query:
        products = Product.objects.filter(
            name__icontains=query,
            is_active=True
        )
    else:
        products = Product.objects.filter(is_active=True)

    categories = Category.objects.all()

    return render(request, 'products/list.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'cart_count': _get_cart_count(request),
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'products/details.html', {
        'product': product,
        'cart_count': _get_cart_count(request),
    })


@admin_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/form.html', {'form': form, 'title': 'Add Product'})


@admin_required
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/form.html', {'form': form, 'title': 'Edit Product'})


@admin_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('product_list')
    return render(request, 'products/confirm_delete.html', {'product': product})