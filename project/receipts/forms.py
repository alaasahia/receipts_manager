from django import forms 
from .models import Receipt

class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['store_name', 'items', 'purchase_date', 'total_ammount']
        widgets = {
            'purchase_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

