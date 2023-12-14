from django.db import models
from django.contrib.auth.models import User
from django.db.models.expressions import fields


class Receipt(models.Model):
    store_name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receipts")
    items = models.TextField()
    purchase_date = models.DateTimeField()
    total_ammount = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, blank=True)

    class Meta:

        indexes = [
            models.Index(
                fields=['store_name','purchase_date'],
                name='store_name_index'
            ),
            models.Index(
                fields=['purchase_date'],
                name='purchase_date_index'
            ),
            models.Index(
                fields=['total_ammount'],
                name='total_ammount_index'
            )
        ]

        constraints = [
            models.UniqueConstraint(
                fields=('user','store_name', 'purchase_date'),
                name='unique_user_receipt'
            )
        ]

    def __str__(self):
        return f'{self.store_name}-{self.purchase_date}'

    

