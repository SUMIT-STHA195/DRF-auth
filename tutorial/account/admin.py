from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser
# Register your models here.


class CustomUserAdmin(UserAdmin):
    model = MyUser()
    list_display = ['email', 'first_name', 'last_name', 'is_staff']
    search_fields = ['email']


admin.site.register(MyUser, CustomUserAdmin)
