# Generated by Django 3.0.5 on 2020-05-09 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0022_auto_20200509_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='first_name',
            field=models.CharField(default='', max_length=50, verbose_name='Adı'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='last_name',
            field=models.CharField(default='', max_length=50, verbose_name='Soyadı'),
        ),
    ]