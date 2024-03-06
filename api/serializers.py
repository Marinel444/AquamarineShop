from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from rest_framework import serializers

from shop.models import Product, Photo


class ProductSerializer(serializers.ModelSerializer):
    photo_set = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "category",
            "sub_category",
            "country",
            "brand",
            "article",
            "description",
            "size",
            "color",
            "material",
            "is_active",
            "stock",
            "price",
            "sale",
            "is_featured",
            "photo_set",

        )

    def create(self, validated_data):
        photos = validated_data.pop("photo_set", [])
        product = Product.objects.create(**validated_data)
        for photo_file in photos:
            try:
                photo = Photo(product=product)
                photo.image.save(photo_file.name, ImageFile(photo_file), save=True)
            except Exception as e:
                product.delete()
                raise e
        return product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "password", "is_staff")
        fields_readonly_fields = ("id", "is_staff")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user
