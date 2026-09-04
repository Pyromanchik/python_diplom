from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from products.models import Product, Supplier
from accounts.models import Contact

User = get_user_model()


class ProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Создаём пользователя-поставщика
        self.supplier_user = User.objects.create(
            first_name='Поставщик',
            last_name='Тест',
            email='supplier_test@example.com',
            role='supplier'
        )
        self.supplier = Supplier.objects.create(
            user=self.supplier_user,
            name='Тестовый поставщик',
            is_accepting_orders=True
        )

        # Создаём пользователя-клиента
        self.client_user = User.objects.create(
            first_name='Иван',
            last_name='Клиент',
            email='client_test@example.com',
            role='client'
        )

        # Создаём товары
        self.product1 = Product.objects.create(
            supplier=self.supplier,
            name='Товар 1',
            description='Описание товара 1',
            price=100.00,
            quantity=50
        )
        self.product2 = Product.objects.create(
            supplier=self.supplier,
            name='Товар 2',
            description='Описание товара 2',
            price=200.00,
            quantity=0
        )

    def _get_paginated_data(self, response):
        """Инструмент для извлечения результатов"""
        return response.data.get('results', response.data)

    def test_list_products(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get('/api/products/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self._get_paginated_data(response)), 2)

    def test_search_products(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get('/api/products/products/?search=Товар 1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = self._get_paginated_data(response)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Товар 1')

    def test_filter_by_supplier(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(f'/api/products/products/?supplier={self.supplier.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self._get_paginated_data(response)), 2)

    def test_filter_by_accepting_orders(self):
        self.supplier.is_accepting_orders = False
        self.supplier.save()

        self.client.force_authenticate(user=self.client_user)
        response = self.client.get('/api/products/products/?supplier__is_accepting_orders=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self._get_paginated_data(response)), 0)

    def test_create_product(self):
        self.client.force_authenticate(user=self.supplier_user)
        data = {
            'name': 'Новый товар',
            'description': 'Описание',
            'price': 150.00,
            'quantity': 30,
        }
        response = self.client.post('/api/products/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_update_product(self):
        self.client.force_authenticate(user=self.supplier_user)
        data = {
            'name': 'Обновлённый товар',
            'description': 'Новое описание',
            'price': 120.00,
            'quantity': 60,
        }
        response = self.client.put(f'/api/products/products/{self.product1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name, 'Обновлённый товар')

    def test_delete_product(self):
        self.client.force_authenticate(user=self.supplier_user)
        response = self.client.delete(f'/api/products/products/{self.product1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 1)


class SupplierTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.supplier_user = User.objects.create(
            first_name='Поставщик',
            last_name='Тест',
            email='supplier_toggle@example.com',
            role='supplier'
        )
        self.supplier = Supplier.objects.create(
            user=self.supplier_user,
            name='Тестовый поставщик',
            is_accepting_orders=True
        )

    def test_toggle_orders(self):
        self.client.force_authenticate(user=self.supplier_user)
        response = self.client.post(f'/api/products/suppliers/{self.supplier.id}/toggle-orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.supplier.refresh_from_db()
        self.assertFalse(self.supplier.is_accepting_orders)

    def test_price_update(self):
        self.client.force_authenticate(user=self.supplier_user)
        data = {'file_url': 'http://example.com/price.xlsx'}
        response = self.client.post('/api/products/price-update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
