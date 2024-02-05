from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from shop.forms import ProductForm, PhotoFormSet
from shop.models import Product, Brand, Category


def index(request):
    categories = (
        Category.objects.prefetch_related(
            "sub_category",
            Prefetch(
                "product",
                queryset=Product.objects.filter(is_featured=True),
                to_attr="featured_products")
        )
    )
    context = {
        "categories": categories,
    }
    return render(request, "index.html", context)


def contact_us(request):
    return render(request, "shop/contact.html")


class ProductFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["photo_formset"] = PhotoFormSet(self.request.POST, self.request.FILES,
                                                    instance=self.object if hasattr(self, "object") else None)
        else:
            context["photo_formset"] = PhotoFormSet(instance=self.object if hasattr(self, "object") else None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context["photo_formset"]
        if photo_formset.is_valid():
            response = super().form_valid(form)
            photo_formset.instance = self.object
            photo_formset.save()
            return response
        else:
            return self.form_invalid(form)


class ProductCreateView(LoginRequiredMixin, ProductFormMixin, generic.CreateView):
    model = Product
    form_class = ProductForm
    template_name = "admin_page/create-product.html"
    success_url = reverse_lazy("shop:shop-list")


class ProductUpdateView(LoginRequiredMixin, ProductFormMixin, generic.UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "admin_page/create-product.html"
    success_url = reverse_lazy("shop:shop-list")


class ProductDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Product
    template_name = "admin_page/confirm-delete-product.html"
    success_url = reverse_lazy("shop:shop-list")


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
        queryset = (
            Product.objects.all()
            .select_related("category", "sub_category", "country", "brand")
            .prefetch_related("photo_set")
        )
        subcategory_slug = self.kwargs.get("slug")
        search_query = self.request.GET.get("search")
        brand_query = self.request.GET.get("brand_name")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if subcategory_slug:
            queryset = queryset.filter(sub_category__slug=subcategory_slug)
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
        brand_ids = self.get_queryset().values_list("brand_id", flat=True).distinct()
        context["brands"] = Brand.objects.filter(id__in=brand_ids)
        context["categories"] = Category.objects.all().prefetch_related("sub_category")
        return context


class Search(generic.ListView):
    model = Product

    template_name = "shop/search.html"
    paginate_by = 9

    def get_queryset(self):
        search_query = self.request.GET.get("search")
        queryset = (
            Product.objects.filter(Q(name__icontains=search_query) | Q(article__icontains=search_query))
            .select_related("category", "sub_category", "country", "brand")
            .prefetch_related("photo_set")
        )
        return queryset
