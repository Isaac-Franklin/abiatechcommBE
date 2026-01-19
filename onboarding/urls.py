from django.urls import path
from . import views

urlpatterns = [
    # auth
    path('userlogin', views.UserLogin, name="UserLogin"),
    path('register', views.UserRegister, name="UserRegister"),
]





