from django.urls import path
from .views import*

app_name = "authapi"

urlpatterns = [
    path('signup', UserRegistration, name = 'signup'),
    path('login', UserLogin, name = 'login'),
    path('changepassword', ChangePassword, name = 'changepassword'),
    path('sendresetpasswordemail',  SendPasswordResetEmail, name = 'sendresetpasswordemail'),
    path('resetpassword/<uid>/<token>', ResetPassword, name = 'resetpassword'),
   
]
