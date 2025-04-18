from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.html import format_html
from django.db.models import Count
from .models import ChatSession, ChatMessage, TrainingDocument, TrainingExample, FinetuningJob


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'applicant_name', 'applicant_email', 'applicant_phone', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('applicant_name', 'applicant_email', 'applicant_phone', 'session_id')
    readonly_fields = ('session_id', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('session_id', 'user', 'created_at', 'updated_at')
        }),
        ('Applicant Information', {
            'fields': ('applicant_name', 'applicant_email', 'applicant_phone', 'vehicle_type', 'driving_experience', 'availability'),
            'classes': ('wide',)
        }),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'timestamp')
    list_filter = ('role', 'timestamp')
    search_fields = ('content', 'session__session_id')
    readonly_fields = ('timestamp',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(TrainingDocument)
class TrainingDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'uploaded_at', 'is_processed_for_training', 'example_count')
    list_filter = ('document_type', 'is_processed_for_training', 'uploaded_at')
    search_fields = ('title', 'description')
    readonly_fields = ('uploaded_at', 'is_processed_for_training', 'example_count')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'document_type')
        }),
        ('File', {
            'fields': ('file', 'uploaded_at', 'is_processed_for_training')
        }),
    )
    
    def example_count(self, obj):
        count = obj.training_examples.count()
        return count
    example_count.short_description = 'Training Examples'
    
    def save_model(self, request, obj, form, change):
        """Process document for fine-tuning after save"""
        super().save_model(request, obj, form, change)
        if not change:  # Only for new documents
            messages.info(request, "Document saved. It will be processed for training examples in the background.")
            # In a real implementation, you would queue a background task here
            # process_document_for_training.delay(obj.id)


@admin.register(TrainingExample)
class TrainingExampleAdmin(admin.ModelAdmin):
    list_display = ('source_document', 'question_preview', 'answer_preview', 'created_at')
    list_filter = ('source_document__document_type', 'created_at')
    search_fields = ('question', 'answer', 'source_document__title')
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'
    
    def answer_preview(self, obj):
        return obj.answer[:50] + '...' if len(obj.answer) > 50 else obj.answer
    answer_preview.short_description = 'Answer'
    
    fieldsets = (
        (None, {
            'fields': ('source_document',)
        }),
        ('Training Example', {
            'fields': ('question', 'answer'),
            'classes': ('wide',)
        }),
    )


@admin.register(FinetuningJob)
class FinetuningJobAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'model_name', 'status', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at', 'model_name')
    readonly_fields = ('job_id', 'training_file_id', 'started_at', 'completed_at')
    
    fieldsets = (
        (None, {
            'fields': ('job_id', 'model_name', 'status')
        }),
        ('Details', {
            'fields': ('training_file_id', 'started_at', 'completed_at')
        }),
    )


# Custom Admin Site with Fine-tuning Dashboard
class ChatbotAdminSite(admin.AdminSite):
    site_header = 'Delivery Driver Recruitment Admin'
    site_title = 'Delivery Driver Recruitment'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fine-tuning/', self.admin_view(self.fine_tuning_view), name='fine-tuning'),
        ]
        return custom_urls + urls
    
    def fine_tuning_view(self, request):
        """Custom admin view for fine-tuning management"""
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'generate_file':
                # Logic to generate fine-tuning file
                messages.success(request, "Fine-tuning file generated successfully.")
                
            elif action == 'submit_job':
                # Logic to submit fine-tuning job to OpenAI
                messages.success(request, "Fine-tuning job submitted successfully.")
        
        # Get training data statistics
        context = {
            'total_documents': TrainingDocument.objects.count(),
            'processed_documents': TrainingDocument.objects.filter(is_processed_for_training=True).count(),
            'total_examples': TrainingExample.objects.count(),
            'example_distribution': TrainingExample.objects.values('source_document__document_type').annotate(count=Count('id')),
            'title': 'Fine-tuning Management',
        }
        
        return render(request, 'admin/fine_tuning.html', context)

# Uncomment to use the custom admin site
# from django.contrib.admin import site
# admin_site = ChatbotAdminSite(name='chatbot_admin')
# admin_site.register(ChatSession, ChatSessionAdmin)
# admin_site.register(ChatMessage, ChatMessageAdmin)
# admin_site.register(TrainingDocument, TrainingDocumentAdmin)
# admin_site.register(TrainingExample, TrainingExampleAdmin)
# admin_site.register(FinetuningJob, FinetuningJobAdmin)