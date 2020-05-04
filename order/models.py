from django.db import models

# Create your models here.
DISTRIBUTION_UNITS = [
    ('piece', 'adet'),
    ('liter', 'litre'),
    ('kilogram', 'kg'),
    ('kangal', 'kangal'),
]

DAYS = [
    ('Sunday', 'Pazartesi'),
    ('Tuesday', 'Salı'),
    ('Wednesday', 'Çarşamba'),
    ('Thursday', 'Perşembe'),
    ('Friday', 'Cuma'),
    ('Saturday', 'Cumartesi'),
    ('Monday', 'Pazar'),
]

class City(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class District(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Neighborhood(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Address(models.Model):
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, verbose_name="İl")
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, verbose_name="İlçe")
    neighborhood = models.ForeignKey(
        Neighborhood, on_delete=models.SET_NULL, null=True, verbose_name="Mahalle")
    address_info = models.TextField(max_length=255, blank=True, null=True, verbose_name="Sokak-Apartman")

    def __str__(self):
        return self.district.name + "-" + self.neighborhood.name + " Mahallesi-" + self.address_info

class Customer(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Adı")
    last_name = models.CharField(max_length=50, verbose_name="Soyadı")
    phone1 = models.CharField(max_length=50, verbose_name="Telefon1")
    phone2 = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telefon2")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name="Adres")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Category(models.Model):
    name = models.CharField(max_length=50,  verbose_name="Kategori Adı")

    createt_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Ürün Kategorisi")
    name = models.CharField(max_length=70, verbose_name="Ürün Adı")
    distribution_unit = models.CharField(
        max_length=255,
        choices=DISTRIBUTION_UNITS,  verbose_name="Dağıtım Birimi"
        )
    price = models.FloatField(verbose_name="Fiyatı")

    createt_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class OrderProduct(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Ürün Adı") 
    order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name="Sipariş")
    distribution_unit = models.CharField(max_length=30, choices=DISTRIBUTION_UNITS, default="piece", verbose_name="Dağıtım Birimi")
    quantity = models.FloatField(verbose_name="Miktar")


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Müşteri Adı")
    products = models.ManyToManyField(Product, through=OrderProduct, verbose_name="Ürünler")
    delivery_day = models.CharField(max_length=50, default="Monday", choices=DAYS, verbose_name="Dağıtım Günü")
    total_amount = models.FloatField(default=0.0, verbose_name="Toplam Tutar")

    createt_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
