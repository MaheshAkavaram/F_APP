# Generated by Django 4.1.3 on 2023-08-04 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0017_alter_order_address_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cod', 'Cash on Delivery'), ('qr_code', 'QR Code'), ('rozerpay', 'Rozer Pay')], max_length=20),
        ),
    ]
