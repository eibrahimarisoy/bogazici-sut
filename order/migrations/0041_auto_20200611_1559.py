# Generated by Django 3.0.5 on 2020-06-11 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0040_auto_20200611_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='nick',
            field=models.CharField(blank=True, max_length=9, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='nick',
            field=models.CharField(blank=True, max_length=14, null=True, unique=True),
        ),
    ]
