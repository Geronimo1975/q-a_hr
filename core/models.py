from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class EditableContent(models.Model):
    """Model for storing editable content with translation support."""
    identifier = models.CharField(max_length=100, unique=True, help_text="Unique identifier for this content piece")
    
    # Content in different languages - these should match the LANGUAGES in settings.py
    content_de = models.TextField(verbose_name=_("German Content"), blank=True)
    content_en = models.TextField(verbose_name=_("English Content"), blank=True)
    content_pl = models.TextField(verbose_name=_("Polish Content"), blank=True)
    content_ro = models.TextField(verbose_name=_("Romanian Content"), blank=True)
    content_uk = models.TextField(verbose_name=_("Ukrainian Content"), blank=True)
    content_ar = models.TextField(verbose_name=_("Arabian Content"), blank=True)
    content_tr = models.TextField(verbose_name=_("Turkish Content"), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Editable Content"
        verbose_name_plural = "Editable Contents"
        ordering = ["identifier"]
    
    def __str__(self):
        return self.identifier
    
    def get_content(self, language_code='de'):
        """Get content in the specified language."""
        language_code = language_code.lower()
        if language_code not in ['de', 'en', 'pl', 'ro', 'uk', 'ar', 'tr']:
            language_code = 'de'  # Default to German
        
        content_field = f'content_{language_code}'
        content = getattr(self, content_field, '')
        
        # If content is empty for the requested language, fall back to German
        if not content and language_code != 'de':
            return self.content_de
        
        return content


class GoogleSheetsConfig(models.Model):
    """Configuration model for Google Sheets integration."""
    enabled = models.BooleanField(default=False, help_text="Enable Google Sheets integration")
    spreadsheet_id = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Google Sheets ID from URL: https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"
    )
    
    # Added header settings
    has_header_row = models.BooleanField(default=True, help_text="First row contains column headers")
    header_row_index = models.IntegerField(default=1, help_text="Row number for headers (1-based)")
    data_start_row = models.IntegerField(default=2, help_text="Row number to start inserting data (1-based)")
    
    # Column mapping defaults
    question_column = models.CharField(
        max_length=10, 
        default="C", 
        help_text="Default column for question text (e.g., 'C')"
    )
    answer_column = models.CharField(
        max_length=10, 
        default="F", 
        help_text="Default column for answers (e.g., 'F')"
    )
    
    class Meta:
        verbose_name = "Google Sheets Configuration"
        verbose_name_plural = "Google Sheets Configuration"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and GoogleSheetsConfig.objects.exists():
            # Update the existing instance
            existing = GoogleSheetsConfig.objects.first()
            existing.enabled = self.enabled
            existing.spreadsheet_id = self.spreadsheet_id
            existing.has_header_row = self.has_header_row
            existing.header_row_index = self.header_row_index
            existing.data_start_row = self.data_start_row
            existing.question_column = self.question_column
            existing.answer_column = self.answer_column
            existing.save()
            return existing
        else:
            return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Google Sheets Configuration (Enabled: {'Yes' if self.enabled else 'No'})"