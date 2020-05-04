# Generated by Django 3.0.5 on 2020-05-03 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0010_auto_20200503_2342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='total_amount',
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='total_amount',
            field=models.FloatField(default=0.0),
        ),
    ]
