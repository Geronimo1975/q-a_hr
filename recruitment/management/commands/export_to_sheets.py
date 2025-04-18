from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CustomUser
from recruitment.models import QuestionStage
from utils.google_sheets import update_sheet_with_answers, create_sheet_if_needed

class Command(BaseCommand):
    help = 'Export all user answers to Google Sheets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--stage',
            type=int,
            help='Export only answers for a specific stage (1-3)',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Export only answers for a specific user (by email)',
        )

    def handle(self, *args, **options):
        if not hasattr(settings, 'GOOGLE_SHEETS') or not settings.GOOGLE_SHEETS.get('enabled', False):
            self.stdout.write(self.style.WARNING('Google Sheets integration is disabled in settings'))
            return
        
        sheet_id = settings.GOOGLE_SHEETS.get('spreadsheet_id')
        if not sheet_id:
            self.stdout.write(self.style.ERROR('No spreadsheet ID specified in settings'))
            return
        
        # Initialize the Google Sheet with the correct tabs and headers
        if not create_sheet_if_needed(sheet_id):
            self.stdout.write(self.style.ERROR('Failed to initialize the Google Sheet'))
            return
        
        # Get users to export
        if options['user']:
            try:
                users = [CustomUser.objects.get(email=options['user'])]
                self.stdout.write(self.style.SUCCESS(f"Found user: {options['user']}"))
            except CustomUser.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with email {options['user']} not found"))
                return
        else:
            users = CustomUser.objects.filter(application_stage__gt=0)
            self.stdout.write(self.style.SUCCESS(f"Found {users.count()} users with applications"))
        
        # Get stages to export
        if options['stage']:
            if options['stage'] < 1 or options['stage'] > 3:
                self.stdout.write(self.style.ERROR("Stage must be between 1 and 3"))
                return
            stages = [options['stage']]
        else:
            stages = list(range(1, 4))  # Stages 1-3
        
        # Export answers for each user and stage
        exported_count = 0
        
        for user in users:
            for stage in stages:
                # Only export if user has reached this stage
                if user.application_stage >= stage:
                    success = update_sheet_with_answers(user, stage, sheet_id)
                    if success:
                        exported_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"Exported answers for user {user.email}, stage {stage}"
                        ))
                    else:
                        self.stdout.write(self.style.ERROR(
                            f"Failed to export answers for user {user.email}, stage {stage}"
                        ))
        
        self.stdout.write(self.style.SUCCESS(f"Export completed. Exported {exported_count} records."))