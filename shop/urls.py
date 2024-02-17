from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from shop.views import (
    index,
    ProductDetailView,
    ProductListView,
    Search,
    ContactView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductOrderView,
    add_to_wishlist_view,
    WishlistView,
    add_to_cart_view,
    CartListView,
    success_view,
)

urlpatterns = [
    path("", index, name="index"),
    path("product/create/", ProductCreateView.as_view(), name="create-product"),
    path("product/<slug:product_slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("product/<slug:product_slug>/update/", ProductUpdateView.as_view(), name="update-product"),
    path("product/<slug:product_slug>/delete/", ProductDeleteView.as_view(), name="delete-product"),
    path("product/<slug:product_slug>/order/", ProductOrderView.as_view(), name="order-product"),
    path("shop/", ProductListView.as_view(), name="shop-list"),
    path(
        "shop/<slug:category_slug>/<slug:subcategory_slug>/",
        ProductListView.as_view(),
        name="product-list"
    ),
    path(
        "shop/<slug:category_slug>/",
        ProductListView.as_view(),
        name="category-product-list"
    ),
    path("search/", Search.as_view(), name="search"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path("wishlist/<int:product_pk>/", add_to_wishlist_view, name="add-wishlist"),
    path("cart/", CartListView.as_view(), name="cart-list"),
    path("cart/<int:product_pk>/", add_to_cart_view, name="add-cart"),
    path("success/", success_view, name="success"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "shop"
