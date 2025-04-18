from django.contrib import admin
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
import csv
from django.utils import timezone
from .models import QuestionStage, Question, Answer, ApplicationSource, ApplicantTracking
from utils.google_sheets import update_sheet_with_answers, create_sheet_if_needed


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(QuestionStage)
class QuestionStageAdmin(admin.ModelAdmin):
    list_display = ('stage_number', 'stage_name')
    search_fields = ('stage_name',)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'stage', 'question_type', 'is_required', 'order')
    list_filter = ('stage', 'question_type', 'is_required')
    search_fields = ('question_text',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer_text', 'submitted_at')
    list_filter = ('question__stage', 'submitted_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'answer_text')
    actions = ['export_as_csv', 'export_to_google_sheets']
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=answers-{timezone.now().strftime("%Y%m%d%H%M%S")}.csv'
        writer = csv.writer(response)
        
        writer.writerow(['User Email', 'Question Stage', 'Question', 'Answer', 'Submitted At'])
        for obj in queryset:
            writer.writerow([
                obj.user.email,
                obj.question.stage.stage_name,
                obj.question.question_text,
                obj.answer_text,
                obj.submitted_at
            ])
        
        return response
    
    export_as_csv.short_description = "Export selected answers as CSV"
    
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
        
        # Get unique users and stages from the selected answers
        user_stage_pairs = set()
        for answer in queryset:
            user_stage_pairs.add((answer.user, answer.question.stage.stage_number))
        
        success_count = 0
        error_count = 0
        
        for user, stage in user_stage_pairs:
            success = update_sheet_with_answers(user, stage, sheet_id)
            if success:
                success_count += 1
            else:
                error_count += 1
        
        if success_count > 0:
            self.message_user(
                request, 
                f"Successfully exported {success_count} user-stage combinations to Google Sheets",
                level=messages.SUCCESS
            )
        
        if error_count > 0:
            self.message_user(
                request, 
                f"Failed to export {error_count} user-stage combinations",
                level=messages.WARNING
            )
    
    export_to_google_sheets.short_description = "Export selected answers to Google Sheets"


@admin.register(ApplicationSource)
class ApplicationSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'tracking_code', 'created_at')
    search_fields = ('name', 'tracking_code')


@admin.register(ApplicantTracking)
class ApplicantTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'source', 'created_at')
    list_filter = ('source', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
