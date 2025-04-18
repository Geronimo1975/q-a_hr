from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'application_stage', 'is_rejected', 'created_at')
    list_filter = ('application_stage', 'is_rejected', 'created_at')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Application Status', {'fields': ('application_stage', 'is_rejected')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'gdpr_consent')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2', 'gdpr_consent'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)
