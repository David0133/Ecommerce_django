from django import forms
from .models import *


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']
    
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone'].widget.attrs['placeholder'] = 'Enter Phone'
        self.fields['email'].widget.attrs['placeholder'] = 'example@gmail.com'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'