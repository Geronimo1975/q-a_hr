from django.contrib import admin
from django.utils.html import format_html
from .models import GoogleSheetsConfig


class GoogleSheetsConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'enabled', 'spreadsheet_id_display')
    readonly_fields = ('spreadsheet_id_display',)
    fieldsets = (
        (None, {
            'fields': ('enabled', 'spreadsheet_id', 'spreadsheet_id_display'),
            'description': 'Configure Google Sheets integration for exporting application data.'
        }),
    )
    
    def spreadsheet_id_display(self, obj):
        if obj.spreadsheet_id:
            return format_html(
                '<a href="https://docs.google.com/spreadsheets/d/{}/edit" target="_blank">'
                'Open Google Sheet</a>',
                obj.spreadsheet_id
            )
        return '—'
    spreadsheet_id_display.short_description = 'Sheet Link'
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not GoogleSheetsConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deleting the configuration
        return False

admin.site.register(GoogleSheetsConfig, GoogleSheetsConfigAdmin)
