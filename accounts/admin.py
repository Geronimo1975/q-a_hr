from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm
from utils.google_sheets import update_sheet_with_answers, create_sheet_if_needed


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'application_stage', 'is_rejected', 'created_at', 'export_button')
    list_filter = ('application_stage', 'is_rejected', 'created_at')
    actions = ['export_to_google_sheets']
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
    
    def export_button(self, obj):
        if obj.application_stage > 0:
            url = reverse('admin:export_user_to_sheets', args=[obj.pk])
            return format_html('<a class="button" href="{}">Export to Sheets</a>', url)
        return "N/A"
    export_button.short_description = "Export to Google Sheets"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/export-to-sheets/',
                self.admin_site.admin_view(self.export_user_to_sheets),
                name='export_user_to_sheets',
            ),
        ]
        return custom_urls + urls
    
    def export_user_to_sheets(self, request, user_id):
        if not settings.GOOGLE_SHEETS.get('enabled', False):
            self.message_user(request, "Google Sheets integration is disabled in settings", level=messages.ERROR)
            return HttpResponseRedirect("../")
        
        sheet_id = settings.GOOGLE_SHEETS.get('spreadsheet_id')
        if not sheet_id:
            self.message_user(request, "No spreadsheet ID specified in settings", level=messages.ERROR)
            return HttpResponseRedirect("../")
        
        # Initialize the Google Sheet with the correct tabs and headers
        if not create_sheet_if_needed(sheet_id):
            self.message_user(request, "Failed to initialize the Google Sheet", level=messages.ERROR)
            return HttpResponseRedirect("../")
            
        try:
            user = CustomUser.objects.get(pk=user_id)
            
            # Only export stages the user has completed
            success_count = 0
            for stage in range(1, user.application_stage + 1):
                if update_sheet_with_answers(user, stage, sheet_id):
                    success_count += 1
            
            if success_count > 0:
                self.message_user(
                    request, 
                    f"Successfully exported data for {user.email} to Google Sheets",
                    level=messages.SUCCESS
                )
            else:
                self.message_user(
                    request, 
                    f"No data was exported for {user.email}",
                    level=messages.WARNING
                )
        except CustomUser.DoesNotExist:
            self.message_user(request, "User not found", level=messages.ERROR)
        
        return HttpResponseRedirect("../")
    
    def export_to_google_sheets(self, request, queryset):
        if not settings.GOOGLE_SHEETS.get('enabled', False):
            self.message_user(request, "Google Sheets integration is disabled in settings", level=messages.ERROR)
            return
        
        sheet_id = settings.GOOGLE_SHEETS.get('spreadsheet_id')
        if not sheet_id:
            self.message_user(request, "No spreadsheet ID specified in settings", level=messages.ERROR)
            return
        
        # Initialize the Google Sheet with the correct tabs and headers
        if not create_sheet_if_needed(sheet_id):
            self.message_user(request, "Failed to initialize the Google Sheet", level=messages.ERROR)
            return
            
        success_count = 0
        skipped_count = 0
        
        for user in queryset:
            if user.application_stage > 0:
                # Export each stage the user has completed
                user_success = False
                for stage in range(1, user.application_stage + 1):
                    if update_sheet_with_answers(user, stage, sheet_id):
                        user_success = True
                
                if user_success:
                    success_count += 1
            else:
                skipped_count += 1
        
        if success_count > 0:
            self.message_user(
                request, 
                f"Successfully exported data for {success_count} users to Google Sheets",
                level=messages.SUCCESS
            )
        
        if skipped_count > 0:
            self.message_user(
                request, 
                f"Skipped {skipped_count} users who haven't started any application stages",
                level=messages.INFO
            )
    
    export_to_google_sheets.short_description = "Export selected users to Google Sheets"


admin.site.register(CustomUser, CustomUserAdmin)
