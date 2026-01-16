from django.urls import path
from .views import ChangePasswordView, LoginUserView, RegisterUserView

app_name = 'Account'


urlpatterns = [
    path("register/", RegisterUserView.as_view(), name='register'),
    path("login/", LoginUserView.as_view(), name="login"),
    path("change-password/",ChangePasswordView.as_view(),name="change-password")
]
