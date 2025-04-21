from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import path
from django.contrib import messages
from .models import GoogleSheetsConfig, EditableContent


class GoogleSheetsConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'enabled', 'spreadsheet_id_display', 'sync_matrix_button', 'sync_questions_button')
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
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'sync_answers_matrix/',
                self.admin_site.admin_view(self.sync_answers_matrix),
                name='sync-answers-matrix',
            ),
            path(
                'sync_questions/',
                self.admin_site.admin_view(self.sync_questions),
                name='sync-questions',
            ),
        ]
        return custom_urls + urls
    
    def sync_answers_matrix(self, request):
        """Sync all answers to the AnswersMatrix sheet"""
        from utils.google_sheets import update_answers_matrix
        
        # Get the active configuration
        config = GoogleSheetsConfig.objects.first()
        if not config or not config.enabled:
            self.message_user(request, "Google Sheets integration is disabled", level=messages.ERROR)
            return HttpResponseRedirect("../")
            
        sheet_id = config.spreadsheet_id
        if not sheet_id:
            self.message_user(request, "No spreadsheet ID configured", level=messages.ERROR)
            return HttpResponseRedirect("../")
            
        # Update the matrix
        result = update_answers_matrix(sheet_id)
        
        if result.get('success'):
            self.message_user(
                request, 
                f"Successfully updated the answers matrix with {result.get('count', 0)} user entries",
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                f"Failed to update answers matrix: {result.get('error', 'Unknown error')}",
                level=messages.ERROR
            )
            
        return HttpResponseRedirect("../")
    
    def sync_questions(self, request):
        """Sync all questions to the Questions sheet"""
        from utils.google_sheets import sync_questions_to_sheets
        
        # Get the active configuration
        config = GoogleSheetsConfig.objects.first()
        if not config or not config.enabled:
            self.message_user(request, "Google Sheets integration is disabled", level=messages.ERROR)
            return HttpResponseRedirect("../")
            
        sheet_id = config.spreadsheet_id
        if not sheet_id:
            self.message_user(request, "No spreadsheet ID configured", level=messages.ERROR)
            return HttpResponseRedirect("../")
            
        # Sync questions
        result = sync_questions_to_sheets()
        
        if result.get('success'):
            self.message_user(
                request, 
                f"Successfully synced {result.get('count', 0)} questions to Google Sheets",
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                f"Failed to sync questions: {result.get('error', 'Unknown error')}",
                level=messages.ERROR
            )
            
        return HttpResponseRedirect("../")
    
    def sync_matrix_button(self, obj):
        if obj.enabled and obj.spreadsheet_id:
            return format_html(
                '<a class="button" href="{}">Sync Answers Matrix</a>',
                'sync_answers_matrix/'
            )
        return '—'
    sync_matrix_button.short_description = 'Matrix Sync'
    
    def sync_questions_button(self, obj):
        if obj.enabled and obj.spreadsheet_id:
            return format_html(
                '<a class="button" href="{}">Sync Questions</a>',
                'sync_questions/'
            )
        return '—'
    sync_questions_button.short_description = 'Questions Sync'
    
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
