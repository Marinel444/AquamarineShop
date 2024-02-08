from django import forms
from .models import Product, Photo


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=14)
    email = forms.EmailField(required=False)
    message = forms.CharField(widget=forms.Textarea)


class OrderForm(forms.Form):
    name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=14)


PhotoFormSet = forms.inlineformset_factory(Product, Photo, fields=("image",), extra=9)

