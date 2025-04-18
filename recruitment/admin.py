from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from django.utils.html import mark_safe
from django.shortcuts import render, get_object_or_404
from django.urls import path, reverse
from django.db import models
import csv
from django.utils import timezone
from .models import QuestionStage, Question, Answer, ApplicationSource, ApplicantTracking
from utils.google_sheets import update_sheet_with_answers, create_sheet_if_needed


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('question_text', 'question_type', 'is_required', 'order', 'choices')
    readonly_fields = ('get_question_count',)
    
    def get_question_count(self, obj):
        return Question.objects.filter(stage=obj.stage).count()
    get_question_count.short_description = "Current Question Count"
    
    def get_extra(self, request, obj=None, **kwargs):
        if obj and Question.objects.filter(stage=obj).count() >= 10:
            return 0  # No extra empty forms if we already have 10 questions
        return self.extra


@admin.register(QuestionStage)
class QuestionStageAdmin(admin.ModelAdmin):
    list_display = ('stage_number', 'stage_name', 'question_count', 'stage_status')
    search_fields = ('stage_name',)
    inlines = [QuestionInline]
    readonly_fields = ('question_count',)
    
    def question_count(self, obj):
        count = Question.objects.filter(stage=obj).count()
        status = "Complete" if count == 10 else "Incomplete"
        return f"{count}/10 ({status})"
    question_count.short_description = "Questions"
    
    def stage_status(self, obj):
        count = Question.objects.filter(stage=obj).count()
        if count < 10:
            return mark_safe('<span style="color: red;">Incomplete (Need 10 questions)</span>')
        elif count > 10:
            return mark_safe('<span style="color: orange;">Too many questions (Limit: 10)</span>')
        return mark_safe('<span style="color: green;">Complete</span>')
    stage_status.short_description = "Status"
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            count = Question.objects.filter(stage=obj).count()
            help_text = f"This stage currently has {count}/10 questions."
            form.base_fields['stage_name'].help_text = help_text
        return form
    
    def save_formset(self, request, form, formset, change):
        """Custom save_formset to enforce the 10 question requirement."""
        instances = formset.save(commit=False)
        
        # Get the stage object
        stage = form.instance
        
        # Count existing questions in this stage (excluding those that will be deleted)
        existing_count = Question.objects.filter(stage=stage).count() - len(formset.deleted_objects)
        
        # Count new questions to be added
        new_count = len([inst for inst in instances if not inst.pk])
        
        # Calculate final count
        final_count = existing_count + new_count
        
        if final_count > 10:
            from django.contrib import messages
            messages.error(request, f"Cannot save. This would result in {final_count} questions, but each stage must have exactly 10 questions.")
            return
        
        # Proceed with the save
        for instance in formset.deleted_objects:
            instance.delete()
        for instance in instances:
            instance.save()
        formset.save_m2m()
        
        # Provide feedback
        remaining = 10 - final_count
        if remaining > 0:
            from django.contrib import messages
            messages.warning(request, f"Stage saved. Please add {remaining} more question(s) to reach the required 10 questions.")


class FileUploadTypeFilter(admin.SimpleListFilter):
    title = 'File Upload Types'
    parameter_name = 'file_type'
    
    def lookups(self, request, model_admin):
        return (
            ('images', 'Images (jpg, png, etc.)'),
            ('documents', 'Documents (pdf, doc, etc.)'),
            ('any', 'Any File Type'),
            ('none', 'No File Uploads'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'images':
            return queryset.filter(question_type='file', allowed_file_types__icontains='jpg') | \
                   queryset.filter(question_type='file', allowed_file_types__icontains='png') | \
                   queryset.filter(question_type='file', allowed_file_types__icontains='jpeg')
        if self.value() == 'documents':
            return queryset.filter(question_type='file', allowed_file_types__icontains='pdf') | \
                   queryset.filter(question_type='file', allowed_file_types__icontains='doc')
        if self.value() == 'any':
            return queryset.filter(question_type='file')
        if self.value() == 'none':
            return queryset.exclude(question_type='file')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'stage', 'question_type', 'get_type_details', 'is_required', 'order', 'reorder_link')
    list_filter = ('stage', 'question_type', 'is_required', FileUploadTypeFilter)
    search_fields = ('question_text',)
    list_editable = ('order',)  # Allow editing order directly in the list view
    actions = ['sync_to_google_sheets']
    fieldsets = (
        (None, {
            'fields': ('stage', 'question_text', 'question_type', 'is_required', 'order')
        }),
        ('Choice Options', {
            'fields': ('choices',),
            'classes': ('collapse',),
            'description': 'For multiple choice questions, provide options separated by semicolons (e.g., "Option 1;Option 2;Option 3")'
        }),
        ('File Upload Settings', {
            'fields': ('allowed_file_types', 'max_file_size'),
            'classes': ('collapse',),
            'description': 'Configure file upload settings (only applicable if question type is "File Upload")'
        }),
    )
    
    def get_urls(self):
        """Add custom URLs for reordering questions and syncing to sheets"""
        urls = super().get_urls()
        custom_urls = [
            path('reorder/', self.admin_site.admin_view(self.reorder_view), 
                 name='recruitment_question_reorder'),
            path('sync-to-sheets/', self.admin_site.admin_view(self.sync_to_sheets_view), 
                 name='recruitment_question_sync_to_sheets'),
        ]
        return custom_urls + urls
    
    def reorder_view(self, request):
        """Custom view for reordering questions with drag and drop"""
        if request.method == 'POST':
            # Process AJAX request for reordering
            question_id = request.POST.get('question_id')
            new_order = request.POST.get('new_order')
            stage_id = request.POST.get('stage_id')
            
            if question_id and new_order:
                # Update the question order
                question = get_object_or_404(Question, id=question_id)
                
                # Get all questions from the same stage
                stage_questions = Question.objects.filter(stage=question.stage).exclude(id=question.id).order_by('order')
                
                # Adjust orders of all questions
                question.order = int(new_order)
                question.save()
                
                # Reorder remaining questions to avoid duplicates
                current_order = 1
                for q in stage_questions:
                    if current_order == int(new_order):
                        current_order += 1
                    q.order = current_order
                    q.save()
                    current_order += 1
                
                return JsonResponse({'status': 'success'})
            
            return JsonResponse({'status': 'error', 'message': 'Invalid parameters'})
            
        # Get all stages and their questions for the template
        stages = QuestionStage.objects.all().order_by('stage_number')
        context = {
            'stages': stages,
            'title': 'Reorder Questions',
            'opts': self.model._meta,
        }
        return render(request, 'admin/recruitment/question/reorder.html', context)
    
    def sync_to_sheets_view(self, request):
        """API endpoint for syncing questions to Google Sheets"""
        from utils.google_sheets import sync_questions_to_sheets
        
        result = sync_questions_to_sheets()
        return JsonResponse(result)
    
    def sync_to_google_sheets(self, request, queryset):
        """Admin action to sync selected questions to Google Sheets"""
        from utils.google_sheets import sync_questions_to_sheets
        
        result = sync_questions_to_sheets()
        if result['success']:
            self.message_user(request, f"Successfully synced {result['count']} questions to Google Sheets", messages.SUCCESS)
        else:
            self.message_user(request, f"Error syncing questions: {result['error']}", messages.ERROR)
    sync_to_google_sheets.short_description = "Sync selected questions to Google Sheets"
    
    def reorder_link(self, obj):
        """Link to the reorder page"""
        url = reverse('admin:recruitment_question_reorder')
        return mark_safe(f'<a href="{url}" class="button">Reorder All</a>')
    reorder_link.short_description = ""
    
    def get_type_details(self, obj):
        if obj.question_type == 'file':
            return f"File Upload ({obj.allowed_file_types if obj.allowed_file_types else 'Any'})"
        elif obj.question_type == 'choice':
            options = obj.choices.split(';') if obj.choices else []
            return f"Choice ({len(options)} options)"
        return obj.get_question_type_display()
    get_type_details.short_description = "Type Details"
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            if obj.question_type == 'file':
                form.base_fields['allowed_file_types'].widget.attrs['placeholder'] = "e.g., pdf,jpg,png"
                form.base_fields['allowed_file_types'].help_text = "Comma-separated list of allowed file extensions"
            elif obj.question_type == 'choice':
                form.base_fields['choices'].widget.attrs['placeholder'] = "Option 1;Option 2;Option 3"
                form.base_fields['choices'].help_text = "Semicolon-separated list of choice options"
        return form
        
    def save_model(self, request, obj, form, change):
        """Override save_model to handle automatic ordering"""
        if not obj.order or obj.order == 0:  # If order is not set
            # Get the maximum order in this stage
            max_order = Question.objects.filter(stage=obj.stage).aggregate(models.Max('order'))['order__max'] or 0
            obj.order = max_order + 1
        
        super().save_model(request, obj, form, change)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'get_answer_display_admin', 'file_link', 'submitted_at')
    list_filter = ('question__stage', 'question__question_type', 'submitted_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'answer_text')
    actions = ['export_as_csv', 'export_to_google_sheets']
    readonly_fields = ('file_preview',)
    
    def get_answer_display_admin(self, obj):
        if obj.question.question_type == 'file' and obj.file_upload:
            return f"File: {obj.file_upload.name.split('/')[-1]}"
        elif obj.question.question_type == 'dob' and obj.answer_text:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(obj.answer_text, '%Y-%m-%d')
                return date_obj.strftime('%d.%m.%Y')
            except:
                return obj.answer_text
        return obj.answer_text[:100] + ('...' if len(obj.answer_text) > 100 else '')
    get_answer_display_admin.short_description = "Answer"
    
    def file_link(self, obj):
        if obj.file_upload:
            return mark_safe(f'<a href="{obj.file_upload.url}" target="_blank">View File</a>')
        return "-"
    file_link.short_description = "File"
    
    def file_preview(self, obj):
        if not obj.file_upload:
            return "No file uploaded"
            
        file_name = obj.file_upload.name.lower()
        if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return mark_safe(f'<img src="{obj.file_upload.url}" style="max-width:300px; max-height:300px" />')
        elif file_name.endswith('.pdf'):
            return mark_safe(f'<a href="{obj.file_upload.url}" target="_blank" class="button">View PDF</a>')
        else:
            return mark_safe(f'<a href="{obj.file_upload.url}" target="_blank" class="button">Download File</a>')
    file_preview.short_description = "File Preview"
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': ('user', 'question', 'answer_text', 'submitted_at')
            })
        ]
        
        # Add file preview if this answer has a file
        if obj and obj.file_upload:
            fieldsets.append(
                ('File Upload', {
                    'fields': ('file_upload', 'file_preview'),
                })
            )
        
        return fieldsets
    
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
