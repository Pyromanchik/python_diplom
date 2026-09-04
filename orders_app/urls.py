from django.urls import path

from . import views

urlpatterns = [
    path('cart/', views.CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', views.CartAddItemView.as_view(), name='cart-add'),
    path('cart/remove/<int:item_id>/', views.CartRemoveItemView.as_view(), name='cart-remove'),
    path('orders/confirm/', views.ConfirmOrderView.as_view(), name='order-confirm'),
    path('orders/', views.OrderHistoryView.as_view(), name='order-history'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
]
