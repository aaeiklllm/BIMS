# Generated by Django 4.2.7 on 2024-10-31 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_userprofile_groups_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='middle_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='midde name'),
        ),
    ]
