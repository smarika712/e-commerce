from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product
from .forms import ProductForm



def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/list.html', {'products': products})


def product_search(request):
    query = request.GET.get('q', '').strip()

    if query:
        products = Product.objects.filter(
            name__icontains=query,
            is_active=True
        )
    else:
        products = Product.objects.filter(is_active=True)

    return render(request, 'products/list.html', {
        'products': products,
        'query': query,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'products/details.html', {'product': product})


@login_required
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


@login_required
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


@login_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('product_list')
    return render(request, 'products/confirm_delete.html', {'product': product})

