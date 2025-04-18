from django.core.management.base import BaseCommand
from django.conf import settings
from utils.google_sheets import create_sheet_if_needed

class Command(BaseCommand):
    help = 'Set up Google Sheet for storing questionnaire responses'

    def handle(self, *args, **options):
        if not hasattr(settings, 'GOOGLE_SHEETS') or not settings.GOOGLE_SHEETS.get('enabled', False):
            self.stdout.write(self.style.WARNING('Google Sheets integration is disabled in settings'))
            return
        
        sheet_id = settings.GOOGLE_SHEETS.get('spreadsheet_id')
        if not sheet_id:
            self.stdout.write(self.style.ERROR('No spreadsheet ID specified in settings'))
            return
        
        success = create_sheet_if_needed(sheet_id)
        if success:
            self.stdout.write(self.style.SUCCESS('Google Sheet has been set up successfully'))
        else:
            self.stdout.write(self.style.ERROR('Failed to set up Google Sheet'))