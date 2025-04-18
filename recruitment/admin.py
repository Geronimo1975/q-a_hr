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
    actions = ['export_as_csv']
    
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


@admin.register(ApplicationSource)
class ApplicationSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'tracking_code', 'created_at')
    search_fields = ('name', 'tracking_code')


@admin.register(ApplicantTracking)
class ApplicantTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'source', 'created_at')
    list_filter = ('source', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
