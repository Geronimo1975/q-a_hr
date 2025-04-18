from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import GoogleSheetsConfig
import os


@receiver(post_save, sender=GoogleSheetsConfig)
def update_google_sheets_settings(sender, instance, **kwargs):
    """Update GOOGLE_SHEETS settings when GoogleSheetsConfig is saved."""
    
    # Update settings
    settings.GOOGLE_SHEETS['enabled'] = instance.enabled
    settings.GOOGLE_SHEETS['spreadsheet_id'] = instance.spreadsheet_id
    
    # Optionally, you could also update environment variables for persistence
    # between restarts (though this won't work in all environments)
    os.environ['GOOGLE_SHEETS_ENABLED'] = str(instance.enabled)
    os.environ['GOOGLE_SHEETS_ID'] = instance.spreadsheet_id