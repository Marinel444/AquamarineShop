from django.db.models import Q
from django.shortcuts import render
from django.views import generic

from shop.models import Product, SubCategory, Brand


def index(request):
    """View function for the home page of the site."""
    products = Product.objects.filter(is_featured=True).prefetch_related("photo_set")
    return render(request, 'index.html', {'products': products})


class ProductDetailView(generic.DetailView):
    model = Product
    queryset = (
        Product.objects.all()
        .select_related("category", "sub_category", "brand", "country")
        .prefetch_related("photo_set")
    )
    template_name = "shop/product-details.html"


class ProductListView(generic.ListView):
    model = Product
    template_name = "shop/product-list.html"
    paginate_by = 9

    def get_queryset(self):
        subcategory_slug = self.kwargs.get("slug")
        search_query = self.request.GET.get("search")
        brand_query = self.request.GET.get("brand_name")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        queryset = (
            Product.objects.filter(sub_category__slug=subcategory_slug)
            .select_related("category", "sub_category", "country", "brand")
            .prefetch_related("photo_set")
        )
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        if brand_query:
            queryset = queryset.filter(brand__name__icontains=brand_query)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.filter(product__isnull=False).distinct()
        return context


class Search(generic.ListView):
    model = Product

    template_name = "shop/search.html"
    paginate_by = 9

    def get_queryset(self):
        search_query = self.request.GET.get("search")
        if search_query:
            queryset = (
                Product.objects.filter(Q(name__icontains=search_query) | Q(article__icontains=search_query))
                .select_related("category", "sub_category", "country", "brand")
                .prefetch_related("photo_set")
            )
        return queryset
