from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail, EmailMessage
from django.db.models import Q, Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import generic

from shop.forms import ProductForm, PhotoFormSet, ContactForm, OrderForm
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
            name = form.cleaned_data["name"]
            phone_number = form.cleaned_data["phone_number"]
            context = {
                "products": products,
                "name": name,
                "phone_number": phone_number,
            }
            html_context = render_to_string("emails/order-for-email.html", context)
            email = EmailMessage(
                "Новый заказ!",
                html_context,
                "aquamarine.solotvino@gmail.com",
                ["aquamarine.solotvino@gmail.com"],
            )
            email.content_subtype = "html"
            email.send()
            request.session["cart"] = []
            return redirect(reverse("shop:index"))
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
        self.object = self.get_object()
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            phone_number = form.cleaned_data["phone_number"]
            context = {
                "products": [self.object],
                "name": name,
                "phone_number": phone_number,
            }
            html_context = render_to_string("emails/order-for-email.html", context)
            email = EmailMessage(
                "Новый заказ!",
                html_context,
                "aquamarine.solotvino@gmail.com",
                ["aquamarine.solotvino@gmail.com"],
            )
            email.content_subtype = "html"
            email.send()
            return redirect(reverse("shop:index"))
        context = self.get_context_data(object=self.object, form=form)
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

    def get_queryset(self):
        queryset = (
            Product.objects.all()
            .select_related("category", "sub_category", "country", "brand")
            .prefetch_related("photo_set")
        )
        category_slug = self.kwargs.get("category_slug")
        subcategory_slug = self.kwargs.get("subcategory_slug")
        search_query = self.request.GET.get("search")
        brand_query = self.request.GET.get("brand_name")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
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
