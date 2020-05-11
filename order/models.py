from django.db import models

# Create your models here.
DISTRIBUTION_UNITS = [
    ('piece', 'Adet'),
    ('liter', 'LT'),
    ('kilogram', 'KG'),
    ('kangal', 'Kangal'),
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


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class District(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    class Meta:
        ordering = ['name']

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

    def get_full_address(self):
        return self.district.name + "-" + self.neighborhood.name + self.address_info

    def __str__(self):
        return self.district.name + "-" + self.neighborhood.name + self.address_info

class Customer(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Adı" ,default="", blank=True)
    last_name = models.CharField(max_length=50, verbose_name="Soyadı", default="", blank=True)
    phone1 = models.CharField(max_length=50, verbose_name="Telefon1")
    phone2 = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telefon2")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name="Adres")

    def __str__(self):
        return f"{self.phone1}"


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
    
    class Meta:
        ordering = ['category']



class OrderProduct(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Ürün Adı") 
    order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name="Sipariş")
    distribution_unit = models.CharField(max_length=30, choices=DISTRIBUTION_UNITS, default="piece", verbose_name="Dağıtım Birimi")
    quantity = models.FloatField(verbose_name="Miktar")


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Müşteri Adı")
    products = models.ManyToManyField(Product, through=OrderProduct, verbose_name="Ürünler")
    delivery_date = models.DateField(blank=True, null=True, verbose_name="Teslimat Tarihi")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Ödeme Şekli")
    total_amount = models.FloatField(default=0.0, verbose_name="Toplam Tutar")
    notes = models.CharField(max_length=50, default="", verbose_name="Notlar")
    delivery_status = models.BooleanField(default=False)
    received_money = models.FloatField(default=0.0)

    is_instagram = models.BooleanField(default=False, verbose_name="İnstagram?")
    instagram_username = models.CharField(max_length=50, null=True, blank=True, help_text="Kullanıcı Adı")
    
    createt_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
