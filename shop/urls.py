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
)

urlpatterns = [
    path("", index, name="index"),
    path("product/create/", ProductCreateView.as_view(), name="create-product"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("product/<slug:slug>/update/", ProductUpdateView.as_view(), name="update-product"),
    path("product/<slug:slug>/delete/", ProductDeleteView.as_view(), name="delete-product"),
    path("product/<slug:slug>/order/", ProductOrderView.as_view(), name="order-product"),
    path("shop/", ProductListView.as_view(), name="shop-list"),
    path("shop/<slug:slug>/", ProductListView.as_view(), name="product-list"),
    path("search/", Search.as_view(), name="search"),
    path("contact/", ContactView.as_view(), name="contact"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "shop"
