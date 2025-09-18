# usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'empresa', 'nivel_acesso')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações da Empresa', {'fields': ('empresa', 'nivel_acesso')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações da Empresa', {'fields': ('empresa', 'nivel_acesso')}),
    )