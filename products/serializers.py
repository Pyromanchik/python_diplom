from rest_framework import serializers
from products.models import Product, Supplier, PriceUpdate


class ProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'supplier', 'supplier_name', 'name', 'description',
                  'characteristics', 'price', 'quantity', 'created_at', 'updated_at')
        read_only_fields = ('supplier', 'created_at', 'updated_at')


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id', 'user', 'name', 'is_accepting_orders', 'created_at')
        read_only_fields = ('user', 'created_at')


class PriceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceUpdate
        fields = ('id', 'supplier', 'file_url', 'updated_at')
        read_only_fields = ('supplier', 'updated_at')
