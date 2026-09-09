from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from accounts.models import Contact
from products.models import Product, Category
from orders_app.models import Cart, CartItem, Order, OrderItem

User = get_user_model()


class CartTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Создаём категорию
        self.category = Category.objects.create(name='Электроника')

        # Создаём пользователя-клиента
        self.client_user = User.objects.create(
            first_name='Иван',
            last_name='Клиент',
            email='client_cart@example.com',
            role='client'
        )
        self.client.force_authenticate(user=self.client_user)

        # Создаём товар
        self.product = Product.objects.create(
            category=self.category,
            name='Товар 1',
            price=100.00,
            quantity=50
        )

    def test_get_or_create_cart(self):
        response = self.client.get('/api/orders/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Cart.objects.count(), 1)

    def test_add_item_to_cart(self):
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post('/api/orders/cart/add/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Cart.objects.count(), 1)
        self.assertEqual(CartItem.objects.count(), 1)
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.quantity, 2)

    def test_add_item_twice(self):
        data = {'product_id': self.product.id, 'quantity': 2}
        self.client.post('/api/orders/cart/add/', data, format='json')
        self.client.post('/api/orders/cart/add/', data, format='json')
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.first().quantity, 4)

    def test_remove_item_from_cart(self):
        data = {'product_id': self.product.id, 'quantity': 2}
        self.client.post('/api/orders/cart/add/', data, format='json')
        cart_item = CartItem.objects.first()
        response = self.client.delete(f'/api/orders/cart/remove/{cart_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CartItem.objects.count(), 0)


class OrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Создаём категорию
        self.category = Category.objects.create(name='Продукты')

        # Создаём пользователя-клиента
        self.client_user = User.objects.create(
            first_name='Иван',
            last_name='Клиент',
            email='client_order@example.com',
            role='client'
        )
        self.contact = Contact.objects.create(
            user=self.client_user,
            first_name='Иван',
            last_name='Клиент',
            email='client@example.com',
            phone='+79991234567',
            address_city='Москва',
            address_street='Ленина',
            address_house='1',
        )
        self.client.force_authenticate(user=self.client_user)

        # Создаём товар
        self.product = Product.objects.create(
            category=self.category,
            name='Товар 1',
            price=100.00,
            quantity=50
        )

    def _get_paginated_data(self, response):
        """Инструмент для извлечения результатов"""
        return response.data.get('results', response.data)

    def test_confirm_order(self):
        # Добавляем товар в корзину
        data = {'product_id': self.product.id, 'quantity': 2}
        self.client.post('/api/orders/cart/add/', data, format='json')
        cart = Cart.objects.get(user=self.client_user, is_completed=False)

        # Подтверждаем заказ
        order_data = {
            'cart_id': cart.id,
            'contact_id': self.contact.id,
        }
        response = self.client.post('/api/orders/orders/confirm/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.total, 200.00)
        self.assertEqual(order.status, 'pending')
        cart.refresh_from_db()
        self.assertTrue(cart.is_completed)

    def test_confirm_empty_cart(self):
        cart = Cart.objects.create(user=self.client_user, is_completed=False)
        order_data = {
            'cart_id': cart.id,
            'contact_id': self.contact.id,
        }
        response = self.client.post('/api/orders/orders/confirm/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_history(self):
        # Создаём заказ вручную
        cart = Cart.objects.create(user=self.client_user, is_completed=True)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
            price_at_add=100.00
        )
        Order.objects.create(
            user=self.client_user,
            cart=cart,
            contact=self.contact,
            total=200.00,
            status='pending',
            number='ORD-TEST-001'
        )

        response = self.client.get('/api/orders/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self._get_paginated_data(response)), 1)

    def test_filter_orders_by_status(self):
        cart1 = Cart.objects.create(user=self.client_user, is_completed=True)
        Order.objects.create(
            user=self.client_user,
            cart=cart1,
            contact=self.contact,
            total=200.00,
            status='pending',
            number='ORD-TEST-002'
        )
        cart2 = Cart.objects.create(user=self.client_user, is_completed=True)
        Order.objects.create(
            user=self.client_user,
            cart=cart2,
            contact=self.contact,
            total=300.00,
            status='confirmed',
            number='ORD-TEST-003'
        )

        response = self.client.get('/api/orders/orders/?status=pending')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self._get_paginated_data(response)), 1)

    def test_order_detail(self):
        cart = Cart.objects.create(user=self.client_user, is_completed=True)
        order = Order.objects.create(
            user=self.client_user,
            cart=cart,
            contact=self.contact,
            total=200.00,
            status='pending',
            number='ORD-TEST-004'
        )

        response = self.client.get(f'/api/orders/orders/{order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['number'], order.number)
