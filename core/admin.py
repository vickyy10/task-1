from django.contrib import admin
from .models import *
from .forms import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(Task)





class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = User

    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser', 'last_login','role','assigned_admin','profile_picture')
    
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password','role','assigned_admin','profile_picture')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name','role','assigned_admin','profile_picture')}
        ),
    )
    
    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)
