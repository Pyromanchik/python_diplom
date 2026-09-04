from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('contacts/', views.ContactListView.as_view(), name='contact-list'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
    path('me/', views.UserDetailView.as_view(), name='user-me'),
]
