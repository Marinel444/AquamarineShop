from django.contrib import admin

from shop.models import (
    Product,
    Category,
    SubCategory,
    Brand,
    Country,
    Photo,
    InstagramPost)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    ordering = ("name", "price", "sale", "size", "sub_category",)
    list_display = ("name", "price", "sale", "size", "sub_category",)
    search_fields = ("name",)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("name", "slug", "category",)
    search_fields = ("name",)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("product", "image",)
    search_fields = ("product__name", )


admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Country)
admin.site.register(InstagramPost)
