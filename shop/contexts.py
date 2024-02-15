from shop.views import Category


def wishlist_count(request):
    wishlist_items = request.session.get("wishlist", [])
    return {
        "wishlist_count": len(wishlist_items),
        "wishlist_items": wishlist_items,
    }


def cart_count(request):
    cart_items = request.session.get("cart", [])
    return {
        "cart_count": len(cart_items),
        "cart_items": cart_items,
    }


def categories_for_html(request):
    categories = Category.objects.all().prefetch_related("sub_category")
    return {"categories": categories}
