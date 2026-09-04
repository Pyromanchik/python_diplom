from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from products.models import Product
from accounts.models import Contact
from orders_app.models import Cart, CartItem, Order, OrderItem
from orders_app.serializers import (
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderHistorySerializer,
)


def get_or_create_active_cart(user):
    cart, created = Cart.objects.get_or_create(
        user=user,
        is_completed=False,
    )
    return cart


class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_or_create_active_cart(self.request.user)


class CartAddItemView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response(
                {'detail': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        with transaction.atomic():
            cart = get_or_create_active_cart(request.user)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={
                    'quantity': quantity,
                    'price_at_add': product.price,
                }
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)


class CartRemoveItemView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return CartItem.objects.get(
            id=self.kwargs['item_id'],
            cart__user=self.request.user,
            cart__is_completed=False,
        )


class ConfirmOrderView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart_id = request.data.get('cart_id')
        contact_id = request.data.get('contact_id')

        if not cart_id or not contact_id:
            return Response(
                {'detail': 'cart_id and contact_id are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart = Cart.objects.get(
                id=cart_id,
                user=request.user,
                is_completed=False,
            )
            contact = request.user.contacts.get(id=contact_id)
        except Cart.DoesNotExist:
            return Response(
                {'detail': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Contact.DoesNotExist:
            return Response(
                {'detail': 'Contact not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not cart.items.exists():
            return Response(
                {'detail': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Generate order number
            order_number = f"ORD-{request.user.id}-{Order.objects.filter(user=request.user).count() + 1:06d}"

            order = Order.objects.create(
                number=order_number,
                user=request.user,
                cart=cart,
                contact=contact,
                total=cart.total,
                status='pending',
            )

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.price_at_add,
                    sum=cart_item.sum,
                )

            cart.is_completed = True
            cart.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items__product__supplier')

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items__product')
