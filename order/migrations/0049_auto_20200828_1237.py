# Generated by Django 3.0.5 on 2020-08-28 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0048_auto_20200828_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='product'),
        ),
    ]
