from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import GoogleSheetsConfig, EditableContent


class GoogleSheetsConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'enabled', 'spreadsheet_id_display')
    readonly_fields = ('spreadsheet_id_display',)
    fieldsets = (
        (None, {
            'fields': ('enabled', 'spreadsheet_id', 'spreadsheet_id_display'),
            'description': 'Configure Google Sheets integration for exporting application data.'
        }),
        ('Row Configuration', {
            'fields': ('has_header_row', 'header_row_index', 'data_start_row'),
            'description': 'Configure row settings for the Google Sheet.',
            'classes': ('collapse',),
        }),
        ('Default Column Mapping', {
            'fields': ('question_column', 'answer_column'),
            'description': 'Set default columns to use for questions and answers. These can be overridden per question.',
            'classes': ('collapse',),
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

class EditableContentAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'updated_at')
    search_fields = ('identifier', 'content_de', 'content_en')
    fieldsets = (
        (None, {
            'fields': ('identifier',),
            'description': 'Unique identifier for this content. This will be used in templates to load this content.'
        }),
        ('Content in Different Languages', {
            'fields': ('content_de', 'content_en', 'content_pl', 'content_ro', 'content_uk', 'content_ar', 'content_tr'),
            'description': 'Enter the content in different languages. If a language is left blank, the German content will be used as fallback.'
        }),
    )

admin.site.register(EditableContent, EditableContentAdmin)
