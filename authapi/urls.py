from django.urls import path
from .views import*

app_name = "authapi"

urlpatterns = [
    path('signup', UserRegistration, name = 'signup'),
    path('login', UserLogin, name = 'login'),
    path('changepassword', ChangePassword, name = 'changepassword'),
    path('sendresetpasswordemail', send_verification_code, name='sendresetpasswordemail'),
    path('resetpassword', reset_password, name='resetpassword'),
]
