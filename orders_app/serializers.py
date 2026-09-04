from rest_framework import serializers
from orders_app.models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    supplier_name = serializers.CharField(source='product.supplier.name', read_only=True)
    sum = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'supplier_name',
                  'quantity', 'price_at_add', 'sum')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'created_at', 'is_completed')


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price', 'sum')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    contact_name = serializers.CharField(
        source='contact.last_name',
        read_only=True
    )

    class Meta:
        model = Order
        fields = ('id', 'number', 'user', 'cart', 'contact', 'contact_name',
                  'items', 'total', 'status', 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at')


class OrderHistorySerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'number', 'total', 'status', 'created_at',
                  'items_count', 'supplier_name')

    def get_items_count(self, obj):
        return obj.items.count()

    def get_supplier_name(self, obj):
        return ', '.join(
            item.product.supplier.name for item in obj.items.all()
        )
