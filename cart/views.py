from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.contrib import messages
from products.models import Product

CART_SESSION_ID = 'cart'

def _get_cart(request):
    return request.session.setdefault(CART_SESSION_ID, {})

def cart_add(request, product_id):
    cart = _get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    pid = str(product.id)
    if pid not in cart:
        cart[pid] = {'quantity': 0, 'price': str(product.price)}
    cart[pid]['quantity'] += 1
    request.session.modified = True
    messages.success(request, f'"{product.name}" added to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

def cart_remove(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session.modified = True
    return redirect('cart_detail')

def cart_update(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    quantity = int(request.POST.get('quantity', 1))
    if pid in cart:
        if quantity > 0:
            cart[pid]['quantity'] = quantity
        else:
            del cart[pid]
        request.session.modified = True
    return redirect('cart_detail')

def cart_detail(request):
    cart = _get_cart(request)
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    items = []
    total = Decimal('0')
    for product in products:
        entry = cart[str(product.id)]
        quantity = entry['quantity']
        price = Decimal(entry['price'])
        subtotal = price * quantity
        total += subtotal
        items.append({'product': product, 'quantity': quantity, 'price': price, 'total_price': subtotal})

    return render(request, 'cart/details.html', {'items': items, 'total': total, 'cart_count': sum(i['quantity'] for i in items)})