from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product


def cart_detail(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total_original = 0
    grand_total = 0

    product_ids = [
        int(key) for key in cart.keys()
        if str(key).isdigit()
    ]

    products = Product.objects.filter(id__in=product_ids)

    for product in products:

        item_data = cart.get(
            str(product.id),
            cart.get(product.id, 1)
        )

        # Support both old and new cart formats
        if isinstance(item_data, dict):
            quantity = item_data.get('quantity', 1)
        else:
            quantity = item_data

        quantity = max(int(quantity), 1)

        # Original price
        raw_old_price = getattr(product, 'old_price', None)

        if raw_old_price is None:
            raw_old_price = product.price or 0

        original_price = float(raw_old_price)
        current_price = float(product.price or 0)

        # Subtotals
        item_original_subtotal = original_price * quantity
        item_subtotal = current_price * quantity

        total_original += item_original_subtotal
        grand_total += item_subtotal

        # Discount percentage
        if original_price > current_price:
            discount_pct = round(
                ((original_price - current_price) / original_price) * 100
            )
        else:
            discount_pct = 0

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'original_price': original_price,
            'subtotal': item_subtotal,
            'original_subtotal': item_original_subtotal,
            'discount_pct': discount_pct,
        })

    total_discount = total_original - grand_total

    context = {
        'cart_items': cart_items,
        'total_original': round(total_original, 2),
        'total_discount': round(total_discount, 2),
        'grand_total': round(grand_total, 2),
        'total_count': sum(
            item['quantity'] for item in cart_items
        ),
    }

    return render(
        request,
        'cart/details.html',
        context
    )


def cart_add(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug
    )

    cart = request.session.get('cart', {})

    product_id = str(product.id)

    if product_id in cart:

        if isinstance(cart[product_id], dict):
            cart[product_id]['quantity'] += 1
        else:
            # Convert old format to new format
            cart[product_id] = {
                'quantity': int(cart[product_id]) + 1
            }

    else:
        cart[product_id] = {
            'quantity': 1
        }

    request.session['cart'] = cart
    request.session.modified = True

    messages.success(
        request,
        f'{product.name} added to cart.'
    )

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            'cart_detail'
        )
    )


def cart_remove(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug
    )

    cart = request.session.get('cart', {})

    product_id = str(product.id)

    if product_id in cart:

        # Full removal (used by the X button)
        if request.GET.get('all') == '1':
            del cart[product_id]

        elif isinstance(cart[product_id], dict):

            quantity = cart[product_id].get(
                'quantity',
                1
            )

            if quantity > 1:
                cart[product_id]['quantity'] = quantity - 1
            else:
                del cart[product_id]

        else:

            if cart[product_id] > 1:
                cart[product_id] -= 1
            else:
                del cart[product_id]

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_detail')