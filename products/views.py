from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from accounts.decorators import admin_required
from .models import Product, Category
from .forms import ProductForm


def _get_wishlist_ids(request):
    """Helper function to get the list of product ids in the session wishlist."""
    return request.session.get('wishlist', [])


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
    request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


# ---------- Product Views ----------

def product_list(request, category_slug=None):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    wishlist_ids = _get_wishlist_ids(request)

    return render(request, 'products/list.html', {
        'products': products,
        'categories': categories,
        'category': category,
        'wishlist_ids': wishlist_ids,
        'wishlist_count': len(wishlist_ids),
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
    wishlist_ids = _get_wishlist_ids(request)

    return render(request, 'products/list.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'wishlist_ids': wishlist_ids,
        'wishlist_count': len(wishlist_ids),
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    wishlist_ids = _get_wishlist_ids(request)

    return render(request, 'products/details.html', {
        'product': product,
        'wishlist_ids': wishlist_ids,
        'wishlist_count': len(wishlist_ids),
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