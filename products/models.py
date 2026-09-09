from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название категории')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Shop(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название магазина')
    categories = models.ManyToManyField(Category, related_name='shops', verbose_name='Категории')

    class Meta:
        verbose_name = 'магазин'
        verbose_name_plural = 'Магазины'
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supplier',
        verbose_name='Пользователь (поставщик)'
    )
    name = models.CharField(max_length=255, verbose_name='Название поставщика')
    is_accepting_orders = models.BooleanField(default=True, verbose_name='Принимает заказы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория',
        blank=True,
        null=True
    )
    name = models.CharField(max_length=255, verbose_name='Наименование')
    description = models.TextField(blank=True, verbose_name='Описание')
    characteristics = models.JSONField(default=dict, verbose_name='Характеристики')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Parameter(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название параметра')

    class Meta:
        verbose_name = 'параметр'
        verbose_name_plural = 'Параметры'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='shop_infos',
        verbose_name='Товар'
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='product_infos',
        verbose_name='Магазин'
    )
    external_id = models.CharField(max_length=255, blank=True, verbose_name='Внешний ID')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.IntegerField(default=0, verbose_name='Количество')

    class Meta:
        verbose_name = 'информация о товаре в магазине'
        verbose_name_plural = 'Информация о товарах в магазинах'
        ordering = ['shop', 'product']
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'shop', 'external_id'],
                name='unique_product_shop_external_id'
            )
        ]

    def __str__(self):
        return f"{self.product.name} ({self.shop.name})"


class ProductParameter(models.Model):
    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        related_name='parameters',
        verbose_name='Информация о товаре'
    )
    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name='product_parameters',
        verbose_name='Параметр'
    )
    value = models.TextField(verbose_name='Значение')

    class Meta:
        verbose_name = 'параметр товара'
        verbose_name_plural = 'Параметры товаров'
        ordering = ['parameter']
        constraints = [
            models.UniqueConstraint(
                fields=['product_info', 'parameter'],
                name='unique_product_info_parameter'
            )
        ]

    def __str__(self):
        return f"{self.product_info.product.name} - {self.parameter.name}: {self.value}"


class PriceUpdate(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='price_updates',
        verbose_name='Поставщик'
    )
    file_url = models.URLField(blank=True, verbose_name='URL файла прайса')
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'обновление прайса'
        verbose_name_plural = 'Обновления прайса'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.supplier.name} - {self.updated_at}"
