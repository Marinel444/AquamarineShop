from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q, Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from shop.forms import ProductForm, PhotoFormSet, ContactForm, OrderForm
from shop.models import Product, Brand, Category, InstagramPost
from shop.utils import send_order_email


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
    instagram_posts = InstagramPost.objects.all()
    context = {
        "categories": categories,
        "instagram_posts": instagram_posts,
    }
    return render(request, "index.html", context)


def success_view(request):
    return render(request, "shop/success.html")


def toggle_item_session(request, product_pk, session_key):
    session_list = request.session.get(session_key, [])
    if product_pk in session_list:
        session_list.remove(product_pk)
    else:
        session_list.append(product_pk)

    request.session[session_key] = session_list
    redirect_url = request.META.get("HTTP_REFERER", "/")
    return HttpResponseRedirect(redirect_url)


def add_to_wishlist_view(request, product_pk):
    return toggle_item_session(request, product_pk, "wishlist")


def add_to_cart_view(request, product_pk):
    return toggle_item_session(request, product_pk, "cart")


class ContactView(generic.edit.FormView):
    template_name = "shop/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy(
        "shop:contact")

    def form_valid(self, form):
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name", "")
        phone_number = form.cleaned_data.get("phone_number")
        email = form.cleaned_data.get("email", "")
        message = form.cleaned_data.get("message")

        full_message = (f"{first_name} {last_name}, \n"
                        f"Телефон: {phone_number}, \n"
                        f"Email: {email}\n"
                        f"Сообщение: {message}")

        send_mail(
            "Обратная связь",
            full_message,
            "aquamarine.solotvino@gmail.com",
            ["aquamarine.solotvino@gmail.com"]
        )

        return super().form_valid(form)


class CartListView(generic.ListView):
    model = Product
    form_class = OrderForm
    template_name = "shop/cart.html"

    def get_queryset(self):
        cart = self.request.session.get("cart", [])
        if cart:
            queryset = (
                Product.objects.filter(pk__in=cart)
                .select_related("country", "brand")
                .prefetch_related("photo_set")
            )
        else:
            queryset = Product.objects.none()
        return queryset

    def post(self, request, *args, **kwargs):
        products = self.get_queryset()
        form = self.form_class(request.POST)
        if form.is_valid():
            send_order_email(
                form.cleaned_data["name"],
                form.cleaned_data["phone_number"],
                products
            )
            request.session["cart"] = []
            return redirect(reverse("shop:success"))
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class ProductOrderView(generic.DetailView):
    model = Product
    form_class = OrderForm
    queryset = (
        Product.objects.all()
        .select_related("category", "sub_category", "brand", "country")
        .prefetch_related("photo_set")
    )
    template_name = "shop/order.html"
    slug_url_kwarg = "product_slug"

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = self.form_class(request.POST)
        if form.is_valid():
            send_order_email(
                form.cleaned_data["name"],
                form.cleaned_data["phone_number"],
                [product]
            )
            return redirect(reverse("shop:success"))
        context = self.get_context_data(object=product, form=form)
        return self.render_to_response(context)


class ProductFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["photo_formset"] = PhotoFormSet(
            instance=self.object if hasattr(self, "object") else None
        )
        if self.request.POST:
            context["photo_formset"] = PhotoFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object if hasattr(self, "object") else None
            )
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
    slug_url_kwarg = "product_slug"


class ProductUpdateView(LoginRequiredMixin, ProductFormMixin, generic.UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "admin_page/create-product.html"
    success_url = reverse_lazy("shop:shop-list")
    slug_url_kwarg = "product_slug"


class ProductDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Product
    template_name = "admin_page/confirm-delete-product.html"
    success_url = reverse_lazy("shop:shop-list")
    slug_url_kwarg = "product_slug"


class ProductDetailView(generic.DetailView):
    model = Product
    queryset = (
        Product.objects.all()
        .select_related("category", "sub_category", "brand", "country")
        .prefetch_related("photo_set")
    )
    template_name = "shop/product-detail.html"
    slug_url_kwarg = "product_slug"


class ProductListView(generic.ListView):
    model = Product
    template_name = "shop/product-list.html"
    paginate_by = 9

    def get_filters(self):
        return {
            "category_slug": self.kwargs.get("category_slug"),
            "subcategory_slug": self.kwargs.get("subcategory_slug"),
            "search_query": self.request.GET.get("search"),
            "brand_query": self.request.GET.get("brand_name"),
            "min_price": self.request.GET.get("min_price"),
            "max_price": self.request.GET.get("max_price"),
            "color_query": self.request.GET.get("color"),
        }

    def get_queryset(self):
        filters = self.get_filters()
        queryset = (
            Product.objects.all()
            .select_related("category", "sub_category", "country", "brand")
            .prefetch_related("photo_set")
        )
        if filters["category_slug"]:
            queryset = queryset.filter(category__slug=filters["category_slug"])
        if filters["subcategory_slug"]:
            queryset = queryset.filter(sub_category__slug=filters["subcategory_slug"])
        if filters["search_query"]:
            queryset = queryset.filter(name__icontains=filters["search_query"])
        if filters["brand_query"]:
            queryset = queryset.filter(brand__name__icontains=filters["brand_query"])
        if filters["min_price"]:
            queryset = queryset.filter(price__gte=filters["min_price"])
        if filters["max_price"]:
            queryset = queryset.filter(price__lte=filters["max_price"])
        if filters["color_query"]:
            queryset = queryset.filter(color__icontains=filters["color_query"])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = self.get_filters()
        brands = Brand.objects.all()
        colors = Product.objects.all()

        if filters["category_slug"]:
            brands = brands.filter(product__category__slug=filters["category_slug"]).distinct()
            colors = colors.filter(category__slug=filters["category_slug"]).distinct()
        if filters["subcategory_slug"]:
            brands = brands.filter(product__sub_category__slug=filters["subcategory_slug"]).distinct()
            colors = colors.filter(sub_category__slug=filters["subcategory_slug"]).distinct()

        context["brands"] = brands
        context["colors"] = colors.values_list("color", flat=True).distinct().order_by("color")
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


class WishlistView(generic.ListView):
    model = Product
    template_name = "shop/wishlist.html"

    def get_queryset(self):
        wishlist = self.request.session.get("wishlist", [])
        if wishlist:
            queryset = (
                Product.objects.filter(pk__in=wishlist)
                .select_related("country", "brand")
                .prefetch_related("photo_set")
            )
        else:
            queryset = Product.objects.none()
        return queryset
