from django import forms
from .models import Product, Photo, Category, SubCategory


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


PhotoFormSet = forms.inlineformset_factory(Product, Photo, fields=("image",), extra=9)

