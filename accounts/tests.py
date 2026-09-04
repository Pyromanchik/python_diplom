from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from accounts.models import Contact

User = get_user_model()


class RegistrationTests(APITestCase):
    def setUp(self):
        self.url = '/api/auth/register/'
        self.data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'password': 'securepass123',
        }

    def test_registration_success(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Token.objects.count(), 1)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)

    def test_registration_missing_fields(self):
        response = self.client.post(self.url, {'email': 'test@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_weak_password(self):
        self.data['password'] = '123'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.url = '/api/auth/login/'
        self.user = User.objects.create(
            first_name='Иван',
            last_name='Иванов',
            email='ivan@example.com',
            role='client'
        )
        self.user.set_password('securepass123')
        self.user.save()

    def test_login_success(self):
        response = self.client.post(self.url, {
            'email': 'ivan@example.com',
            'password': 'securepass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_wrong_password(self):
        response = self.client.post(self.url, {
            'email': 'ivan@example.com',
            'password': 'wrongpassword',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        response = self.client.post(self.url, {
            'email': 'nonexistent@example.com',
            'password': 'password',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ContactTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            first_name='Иван',
            last_name='Иванов',
            email='ivan_contact@example.com',
            role='client'
        )
        self.user.set_password('securepass123')
        self.user.save()
        self.client.force_authenticate(user=self.user)
        self.url = '/api/auth/contacts/'

    def _get_paginated_data(self, response):
        """Инструмент для извлечения результатов"""
        return response.data.get('results', response.data)

    def test_create_contact(self):
        data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'middle_name': 'Иванович',
            'email': 'ivan@example.com',
            'phone': '+79991234567',
            'address_city': 'Москва',
            'address_street': 'Ленина',
            'address_house': '1',
            'address_building': 'А',
            'address_structure': '1',
            'address_apartment': '10',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)

    def test_list_contacts(self):
        Contact.objects.create(
            user=self.user,
            first_name='Иван',
            last_name='Иванов',
            email='ivan@example.com',
            phone='+79991234567',
            address_city='Москва',
            address_street='Ленина',
            address_house='1',
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self._get_paginated_data(response)), 1)

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
