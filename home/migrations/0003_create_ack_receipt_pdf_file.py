# Generated by Django 5.1.3 on 2024-11-26 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_request_sample_sample'),
    ]

    operations = [
        migrations.AddField(
            model_name='create_ack_receipt',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='ack_receipts/'),
        ),
    ]