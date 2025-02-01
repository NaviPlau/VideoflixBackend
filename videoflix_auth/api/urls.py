from django.urls import path
from . import views

urlpatterns = [
  path('register/', views.RegistrationView.as_view(), name='register'),
  path('activate/<str:uidb64>/<str:token>/', views.ActivateAccountView.as_view(), name='activate'),
  path('reset-password/', views.PasswordResetView.as_view(), name='password_reset'),
  path('reset-password/confirm/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
  path('login/', views.LoginView.as_view(), name='login'),
  path('remember-login/', views.TokenLoginView.as_view(), name='token_login'),
]
