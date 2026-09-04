from decimal import Decimal

from django.db import models
from django.conf import settings


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_completed = models.BooleanField(default=False, verbose_name='Завершена')

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-created_at']

    def __str__(self):
        return f"Корзина {self.user} (completed={self.is_completed})"

    @property
    def total(self):
        return sum(item.sum for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.IntegerField(default=1, verbose_name='Количество')
    price_at_add = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена при добавлении'
    )

    class Meta:
        verbose_name = 'элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        ordering = ['id']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def sum(self):
        return self.price_at_add * self.quantity


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает обработки'),
        ('confirmed', 'Подтверждён'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    )

    number = models.CharField(max_length=50, unique=True, verbose_name='Номер заказа')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Корзина'
    )
    contact = models.ForeignKey(
        'accounts.Contact',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Контакт'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Итого'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.number}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.IntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        ordering = ['id']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
