from django.db import models
from django.conf import settings


class GoogleSheetsConfig(models.Model):
    """Configuration model for Google Sheets integration."""
    enabled = models.BooleanField(default=False, help_text="Enable Google Sheets integration")
    spreadsheet_id = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Google Sheets ID from URL: https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"
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
            existing.save()
            return existing
        else:
            return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Google Sheets Configuration (Enabled: {'Yes' if self.enabled else 'No'})"