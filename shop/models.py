from django.db import models
from django.utils.text import slugify

from shop.utils import ukrainian_to_latin


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    photo = models.ImageField(upload_to="img/category_photo/", default="img/icon-default.png")

    class Meta:
        ordering = ("name",)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name="sub_category", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            translate_slug = ukrainian_to_latin(self.name)
            self.slug = slugify(translate_slug, allow_unicode=True)
        super(SubCategory, self).save(*args, **kwargs)

    class Meta:
        ordering = ("name",)
        verbose_name = "Суб_Категория"
        verbose_name_plural = "Суб_Категории"

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="img/brand_photo/", blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        Category,
        related_name="product",
        on_delete=models.CASCADE
    )
    sub_category = models.ForeignKey(
        SubCategory,
        related_name="product",
        blank=True,
        on_delete=models.CASCADE
    )
    country = models.ForeignKey(
        Country,
        related_name="product",
        on_delete=models.CASCADE
    )
    brand = models.ForeignKey(
        Brand,
        related_name="product",
        on_delete=models.CASCADE
    )
    article = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    size = models.CharField(max_length=12, blank=True)
    color = models.CharField(max_length=100, blank=True)
    material = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    meta_description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name


class Photo(models.Model):
    product = models.ForeignKey(Product, verbose_name="photo", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=f"product/%Y/%m/%d/")
