# Generated by Django 5.1.1 on 2024-09-26 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userprofile_deletion_requested'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='deletion_approved',
            field=models.BooleanField(default=False, verbose_name='Deletion Approved'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='deletion_requested',
            field=models.BooleanField(default=False, verbose_name='Deletion Requested'),
        ),
    ]
