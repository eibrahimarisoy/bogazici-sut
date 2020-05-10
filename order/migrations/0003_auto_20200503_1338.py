# Generated by Django 3.0.5 on 2020-05-03 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20200503_1118'),
    ]

    operations = [
        migrations.RenameField(
            model_name='neighborhood',
            old_name='township',
            new_name='district',
        ),
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.Address', verbose_name='Adres'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='first_name',
            field=models.CharField(max_length=50, verbose_name='Adı'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='last_name',
            field=models.CharField(max_length=50, verbose_name='Soyadı'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone1',
            field=models.CharField(max_length=50, verbose_name='Telefon1'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone2',
            field=models.CharField(max_length=50, verbose_name='Telefon2'),
        ),
    ]