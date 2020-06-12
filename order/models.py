from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

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


class City(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class District(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    nick = models.CharField(max_length=4, null=True, blank=True, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Neighborhood(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    class Meta:
        ordering = ['name']

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
        return self.district.name + "-" + self.neighborhood.name + "-" + self.address_info

    def __str__(self):
        return f"{self.district.name.upper()} {self.neighborhood.name.upper()} {self.address_info.upper()}"

class Customer(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Adı" ,default="", blank=True)
    last_name = models.CharField(max_length=50, verbose_name="Soyadı", default="", blank=True)
    nick = models.CharField(max_length=9, null=True, blank=True, unique=True)
    phone1 = models.CharField(max_length=50, verbose_name="Telefon1", unique=True)
    phone2 = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telefon2")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name="Adres")

    def __str__(self):
        return f"{self.nick}"

    class Meta:
        ordering = ['phone1']

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
    purchase_price = models.FloatField(verbose_name="Alış Fiyatı", blank=True, null=True)

    createt_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    class Meta:
        ordering = ['category']


class OrderItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Ürün Adı")
    price = models.FloatField(default=0)
    # order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name="Sipariş")
    is_deleted = models.BooleanField(default=False)
    quantity = models.FloatField(verbose_name="Miktar", validators=[MinValueValidator(0.1)])

    createt_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} price: {self.price} TL"


class Order(models.Model):
    class PaymentMethodEnum(models.IntegerChoices):
        CASH = 1, 'Nakit'
        EFT = 2, 'EFT'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Müşteri Adı")
    nick =  models.CharField(max_length=14, null=True, blank=True, unique=True)
    items = models.ManyToManyField(OrderItem, verbose_name="Ürünler", related_name='order_item')

    delivery_date = models.DateField(blank=True, null=True, verbose_name="Teslimat Tarihi")
    payment_method = models.PositiveSmallIntegerField(
        choices=PaymentMethodEnum.choices,
        blank=True,
        null=True,
        verbose_name="Ödeme Şekli"
    )
    total_price = models.FloatField(default=0, verbose_name="Toplam Tutar")
    notes = models.CharField(max_length=50, default="", verbose_name="Notlar", blank=True, null=True)
    is_delivered = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    received_money = models.FloatField(default=0.0)
    remaining_debt = models.FloatField(default=0.0)
    service_fee = models.FloatField(default=0.0)

    is_instagram = models.BooleanField(default=False, verbose_name="İnstagram?")
    instagram_username = models.CharField(max_length=50, null=True, blank=True, help_text="Kullanıcı Adı")
    
    createt_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PK: {self.pk} - Total: {self.total_price} - Delivered: {self.is_delivered}"

    def total_price_update(self):
        if not self.is_delivered:
            total_price = 0
            for item in self.items.all():
                if item.is_deleted == False:
                    total_price += item.price * item.quantity
            self.total_price = total_price

    class Meta:
        ordering = ['-delivery_date']

@receiver(post_save, sender=OrderItem)
def order_item_receiver(sender, instance, created, *args, **kwargs):
    if created:
        instance.price = instance.product.price
        instance.save()
    if instance.order_item.last() is not None:
        instance.price = instance.product.price
        instance.order_item.last().total_price_update()


@receiver(m2m_changed, sender=Order.items.through)
def order_receiver(sender, instance, *args, **kwargs):
    instance.total_price_update()


@receiver(post_save, sender=Product)
def order_item_receiver_for_update(sender, instance, *args, **kwargs):
    for item in instance.orderitem_set.all():
        item.price = instance.price
        item.save()
