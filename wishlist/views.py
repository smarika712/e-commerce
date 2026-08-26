from django.shortcuts import render
from products.models import Product


def wishlist_detail(request):
    wishlist_ids = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist_ids, is_active=True)

    return render(request, 'wishlist/detail.html', {
        'products': products,
        'wishlist_count': len(wishlist_ids),
    })