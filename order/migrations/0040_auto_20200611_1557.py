# Generated by Django 3.0.5 on 2020-06-11 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0039_order_nick'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='nick',
            field=models.CharField(blank=True, max_length=4, null=True, unique=True),
        ),
    ]
