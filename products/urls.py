from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('suppliers/<int:pk>/toggle-orders/', views.SupplierToggleOrdersView.as_view(), name='supplier-toggle'),
    path('suppliers/<int:pk>/orders/', views.SupplierOrdersView.as_view(), name='supplier-orders'),
    path('price-update/', views.PriceUpdateView.as_view(), name='price-update'),
]
