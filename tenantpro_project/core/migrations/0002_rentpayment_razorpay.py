from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentpayment',
            name='razorpay_order_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='rentpayment',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='rentpayment',
            name='razorpay_signature',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='rentpayment',
            name='payment_method',
            field=models.CharField(
                blank=True,
                choices=[
                    ('upi', 'UPI'), ('bank_transfer', 'Bank Transfer'),
                    ('cash', 'Cash'), ('cheque', 'Cheque'), ('razorpay', 'Razorpay')
                ],
                max_length=20
            ),
        ),
    ]
