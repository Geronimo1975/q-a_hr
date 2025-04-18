from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    google_sheet_updated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Applicant information that might be extracted from chat
    applicant_name = models.CharField(max_length=255, blank=True, null=True)
    applicant_email = models.EmailField(blank=True, null=True)
    applicant_phone = models.CharField(max_length=20, blank=True, null=True)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    driving_experience = models.CharField(max_length=100, blank=True, null=True)
    availability = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        if self.user:
            return f"Chat Session - {self.user.email} ({self.session_id})"
        return f"Chat Session - Anonymous ({self.session_id})"
    
    def update_google_sheet(self):
        """Update Google Sheet with applicant data"""
        # Implementation for Google Sheet update
        pass


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.role}: {self.content[:30]}..."
    
    class Meta:
        ordering = ['timestamp']


class TrainingDocument(models.Model):
    """Model for storing training documents for chatbot fine-tuning"""
    DOCUMENT_TYPES = (
        ('policy', 'Policy Document'),
        ('faq', 'FAQ Document'),
        ('guide', 'Training Guide'),
        ('script', 'Conversation Script'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='training_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed_for_training = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title


class TrainingExample(models.Model):
    """Individual training examples extracted from documents"""
    source_document = models.ForeignKey(TrainingDocument, on_delete=models.CASCADE, related_name='training_examples')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Example from {self.source_document.title}"


class FinetuningJob(models.Model):
    """Record of fine-tuning jobs submitted to OpenAI"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    job_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    model_name = models.CharField(max_length=100)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    training_file_id = models.CharField(max_length=255)
    
    def __str__(self):
        return f"Fine-tuning Job {self.job_id} - {self.status}"