def cart_context(request):
    cart = request.session.get('cart', {})

    count = 0
    for item_data in cart.values():
        if isinstance(item_data, dict):
            count += item_data.get('quantity', 1)
        else:
            count += item_data

    return {'cart_count': count}