# Generated by Django 4.2.8 on 2023-12-14 10:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("receipts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="receipt",
            name="purchase_date",
            field=models.DateTimeField(),
        ),
    ]
