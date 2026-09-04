from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'client'),
        ('supplier', 'supplier'),
        ('admin', 'admin'),
    )

    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=150, blank=True, verbose_name='Отчество')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client', verbose_name='Роль')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.email})"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0] if '@' in self.email else 'user'
        super().save(*args, **kwargs)


class Contact(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='Пользователь'
    )
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=150, blank=True, verbose_name='Отчество')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address_city = models.CharField(max_length=255, verbose_name='Город')
    address_street = models.CharField(max_length=255, verbose_name='Улица')
    address_house = models.CharField(max_length=50, verbose_name='Дом')
    address_building = models.CharField(max_length=50, blank=True, verbose_name='Корпус')
    address_structure = models.CharField(max_length=50, blank=True, verbose_name='Строение')
    address_apartment = models.CharField(max_length=50, blank=True, verbose_name='Квартира')

    class Meta:
        verbose_name = 'контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['-id']

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.phone}"
