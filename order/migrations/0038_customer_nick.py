# Generated by Django 3.0.5 on 2020-06-11 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0037_district_nick'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='nick',
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
    ]
