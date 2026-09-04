from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from products.models import Product, Supplier, PriceUpdate
from products.serializers import (
    ProductSerializer,
    SupplierSerializer,
    PriceUpdateSerializer,
)


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related('supplier').all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'supplier__is_accepting_orders']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(supplier=self.request.user.supplier)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('supplier').all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class SupplierToggleOrdersView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.supplier

    def post(self, request, *args, **kwargs):
        supplier = self.get_object()
        supplier.is_accepting_orders = not supplier.is_accepting_orders
        supplier.save()
        return Response(
            {'is_accepting_orders': supplier.is_accepting_orders},
            status=status.HTTP_200_OK,
        )


class SupplierOrdersView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        supplier = self.request.user.supplier
        return Product.objects.filter(
            supplier=supplier,
            quantity__gt=0
        )


class PriceUpdateView(generics.CreateAPIView):
    serializer_class = PriceUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(supplier=self.request.user.supplier)
