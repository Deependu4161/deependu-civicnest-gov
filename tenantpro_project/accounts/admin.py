from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username','email','role','first_name','last_name','date_joined']
    list_filter = ['role','is_staff']
    fieldsets = UserAdmin.fieldsets + (('TenantPro',{'fields':('role','phone','avatar_initials')}),)
