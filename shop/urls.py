from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from shop.views import index, ProductDetailView, ProductListView, Search

urlpatterns = [
    path("", index, name="index"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("subcategory/<slug:slug>/", ProductListView.as_view(), name="product-list"),
    path("search/", Search.as_view(), name="search"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "shop"
