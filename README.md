# Автоматизация закупок в розничной сети

REST API сервис для автоматизации закупок товаров в розничной сети через Django REST Framework.

## Описание проекта

Сервис позволяет:
- **Клиентам (покупателям)** делать ежедневные закупки по каталогу товаров от разных поставщиков
- **Поставщикам** управлять прайс-листами, принимать/отклонять заказы, просматривать заказы с их товарами
- Поддержка авторизации, регистрации и восстановления пароля через API

## Архитектура

Проект разделён на 3 приложения (apps):

### accounts — Управление пользователями
- Кастомная модель пользователя `CustomUser` с ролями (client, supplier, admin)
- Контакты пользователей с полными адресами
- Аутентификация через Token Authentication

### products — Каталог товаров
- Поставщики с возможностью включения/отключения приёма заказов
- Товары с характеристиками (JSON), ценой, количеством
- Логирование обновлений прайс-листов

### orders_app — Корзина и заказы
- Корзина с добавлением/удалением товаров
- Подтверждение заказов с привязкой контактов
- История заказов с фильтрацией по статусу и дате

## Технологии

- **Python 3.10+**
- **Django 4.2**
- **Django REST Framework 3.14**
- **PostgreSQL**
- **django-filter 23.5**
- **Token Authentication**

## Установка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd python_diplom
```

### 2. Виртуальное окружение
```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных

Создайте базу данных в PostgreSQL:
```sql
CREATE DATABASE orders;
```

Настройте подключение в `orders/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'orders',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Миграции
```bash
python manage.py migrate
```

### 6. Запуск сервера
```bash
python manage.py runserver
```

## API Endpoints

### Аутентификация (`/api/auth/`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/register/` | Регистрация пользователя |
| `POST` | `/login/` | Авторизация, получение token |
| `POST` | `/password-reset/` | Запрос сброса пароля |

### Контакты (`/api/auth/contacts/`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/` | Список контактов пользователя |
| `POST` | `/` | Создание контакта |
| `GET` | `/<id>/` | Детали контакта |
| `PUT` | `/<id>/` | Обновление контакта |
| `DELETE` | `/<id>/` | Удаление контакта |

### Товары (`/api/products/`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/products/` | Каталог товаров (с фильтрацией и поиском) |
| `GET` | `/products/<id>/` | Детали товара |
| `POST` | `/products/` | Создание товара (только поставщик) |
| `PUT` | `/products/<id>/` | Обновление товара |
| `DELETE` | `/products/<id>/` | Удаление товара |
| `POST` | `/suppliers/<id>/toggle-orders/` | Вкл/выкл приём заказов |
| `POST` | `/price-update/` | Обновление прайса |

**Параметры фильтрации товаров:**
- `supplier` — фильтр по поставщику
- `supplier__is_accepting_orders` — фильтр по активному приёму заказов
- `search` — поиск по названию и описанию
- `ordering` — сортировка (`price`, `name`, `created_at`)

### Заказы (`/api/orders/`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/cart/` | Текущая корзина пользователя |
| `POST` | `/cart/add/` | Добавить товар в корзину |
| `DELETE` | `/cart/remove/<item_id>/` | Удалить товар из корзины |
| `POST` | `/orders/confirm/` | Подтверждение заказа |
| `GET` | `/orders/` | История заказов |
| `GET` | `/orders/<id>/` | Детали заказа |

**Параметры фильтрации заказов:**
- `status` — фильтр по статусу (`pending`, `confirmed`, `shipped`, `delivered`, `cancelled`)
- `date_from` — дата от
- `date_to` — дата до
- `ordering` — сортировка (`created_at`, `total`)

## Структура проекта

```
python_diplom/
├── accounts/              # Пользователи, аутентификация, контакты
│   ├── models.py          # CustomUser, Contact
│   ├── serializers.py     # Сериализаторы для API
│   ├── views.py           # API views
│   ├── urls.py            # URL routing
│   └── tests.py           # Тесты
├── products/              # Каталог товаров, поставщики
│   ├── models.py          # Supplier, Product, PriceUpdate
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── orders_app/            # Корзина, заказы
│   ├── models.py          # Cart, CartItem, Order, OrderItem
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── orders/                # Настройки проекта
│   ├── settings.py        # Конфигурация Django
│   ├── urls.py            # Корневой URL routing
│   └── wsgi.py
├── requirements.txt       # Зависимости
├── manage.py
└── README.md
```

## Тесты

Запуск всех тестов:
```bash
python manage.py test
```

Запуск тестов для конкретного приложения:
```bash
python manage.py test accounts
python manage.py test products
python manage.py test orders_app
```

## Этап 1: Выполненные задачи

### Создано
- ✅ Django-проект с виртуальным окружением
- ✅ 3 приложения: `accounts`, `products`, `orders_app`
- ✅ Настройка PostgreSQL в качестве базы данных
- ✅ Django REST Framework с Token Authentication
- ✅ Фильтрация и поиск через django-filter

### Модели данных
- ✅ CustomUser с ролями (client, supplier, admin)
- ✅ Contact с полными адресами
- ✅ Supplier с управлением приёмом заказов
- ✅ Product с JSON-характеристиками
- ✅ Cart, CartItem, Order, OrderItem

### API
- ✅ Регистрация и авторизация
- ✅ CRUD контактов
- ✅ Каталог товаров с фильтрацией
- ✅ Корзина (добавление, удаление)
- ✅ Подтверждение заказов
- ✅ История заказов с фильтрацией

### Тесты
- ✅ 27 тестов, все проходят успешно
- ✅ Покрытие основных сценариев

## Дальнейшие задачи (Этап 2)
- Импорт товаров из файлов (CSV, Excel)
- Уведомления поставщиков о новых заказах
- Email-уведомления клиентам
- Расширенное управление ролями и правами
- Оптимизация запросов к БД
