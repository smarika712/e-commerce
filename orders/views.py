import base64
import json
import uuid as uuid_lib

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from products.models import Product
from .models import Order, OrderItem
from .esewa import generate_esewa_signature, verify_esewa_signature, ESEWA_FORM_URL, ESEWA_PRODUCT_CODE


def _get_cart_items(request):
    cart = request.session.get('cart', {})

    product_ids = [int(key) for key in cart.keys() if str(key).isdigit()]
    products = Product.objects.filter(id__in=product_ids)

    items = []
    total = 0

    for product in products:
        item_data = cart.get(str(product.id), 1)
        quantity = item_data.get('quantity', 1) if isinstance(item_data, dict) else item_data
        quantity = max(int(quantity), 1)

        price = float(product.price or 0)
        subtotal = price * quantity
        total += subtotal

        items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal,
        })

    return items, round(total, 2)


@login_required
def checkout(request):
    cart_items, total = _get_cart_items(request)

    if not cart_items:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart_detail')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        payment_method = request.POST.get('payment_method')

        if not all([full_name, phone, address, city, payment_method]):
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'orders/checkout.html', {
                'cart_items': cart_items,
                'total': total,
            })

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            payment_method=payment_method,
            total_amount=total,
            status=Order.STATUS_COD if payment_method == Order.PAYMENT_COD else Order.STATUS_PENDING,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].name,
                price=item['price'],
                quantity=item['quantity'],
            )

        if payment_method == Order.PAYMENT_COD:
            request.session['cart'] = {}
            request.session.modified = True
            messages.success(request, 'Order placed successfully! Pay on delivery.')
            return redirect('order_success', order_id=order.order_id)

        # ---- eSewa flow ----
        transaction_uuid = str(uuid_lib.uuid4())
        order.esewa_transaction_uuid = transaction_uuid
        order.save()

        signature = generate_esewa_signature(
            total_amount=total,
            transaction_uuid=transaction_uuid,
        )

        esewa_context = {
            'esewa_form_url': ESEWA_FORM_URL,
            'amount': total,
            'tax_amount': 0,
            'total_amount': total,
            'transaction_uuid': transaction_uuid,
            'product_code': ESEWA_PRODUCT_CODE,
            'product_service_charge': 0,
            'product_delivery_charge': 0,
            'success_url': request.build_absolute_uri('/orders/esewa/verify/'),
            'failure_url': request.build_absolute_uri('/orders/esewa/failure/'),
            'signed_field_names': 'total_amount,transaction_uuid,product_code',
            'signature': signature,
        }

        return render(request, 'orders/esewa_redirect.html', esewa_context)

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total': total,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'orders/success.html', {'order': order})


@csrf_exempt
def esewa_verify(request):
    """eSewa redirects here (GET) after payment with a base64-encoded 'data' param."""
    encoded_data = request.GET.get('data')

    if not encoded_data:
        messages.error(request, 'Invalid payment response.')
        return redirect('cart_detail')

    try:
        decoded_bytes = base64.b64decode(encoded_data)
        data = json.loads(decoded_bytes)
    except Exception:
        messages.error(request, 'Could not verify payment response.')
        return redirect('cart_detail')

    if not verify_esewa_signature(data):
        messages.error(request, 'Payment signature verification failed.')
        return redirect('cart_detail')

    transaction_uuid = data.get('transaction_uuid')
    status = data.get('status')

    order = get_object_or_404(Order, esewa_transaction_uuid=transaction_uuid)

    if status == 'COMPLETE':
        order.status = Order.STATUS_PAID
        order.save()

        request.session['cart'] = {}
        request.session.modified = True

        messages.success(request, 'Payment successful!')
        return redirect('order_success', order_id=order.order_id)
    else:
        order.status = Order.STATUS_FAILED
        order.save()
        messages.error(request, 'Payment was not completed.')
        return redirect('cart_detail')


def esewa_failure(request):
    messages.error(request, 'Payment was cancelled or failed.')
    return redirect('cart_detail')