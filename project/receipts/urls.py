from django.contrib import admin
from django.urls import include, path
from .views import ReceiptFormView, ReceiptListView, ReceiptDetailView, delete_receipt, delete_receipt, get_store_names
urlpatterns = [
    path('', ReceiptListView.as_view(), name='user_receipts'),
    path('create/', ReceiptFormView.as_view(), name='create_receipt'),
    path('<int:receipt_id>/', ReceiptDetailView.as_view(), name='receipt_details'),
    path('<int:receipt_id>/edit/', ReceiptFormView.as_view(), name='update_receipt'),
    path('<int:receipt_id>/delete/', delete_receipt, name='delete_receipt'),
    path('store_names/', get_store_names, name='store_names')
]
