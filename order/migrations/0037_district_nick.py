# Generated by Django 3.0.5 on 2020-06-11 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0036_auto_20200611_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='nick',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
