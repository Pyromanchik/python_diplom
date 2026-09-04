from django.db import models
from django.conf import settings


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
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Поставщик'
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
