from django.db import models
from accounts.models import CustomUser


class QuestionStage(models.Model):
    stage_number = models.IntegerField(unique=True)
    stage_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Stage {self.stage_number}: {self.stage_name}"


class Question(models.Model):
    QUESTION_TYPES = (
        ('text', 'Text Input'),
        ('number', 'Number Input'),
        ('choice', 'Multiple Choice'),
        ('boolean', 'Yes/No'),
        ('file', 'File Upload'),
        ('name', 'Full Name'),
        ('dob', 'Date of Birth'),
        ('address', 'Address'),
        ('phone', 'Phone Number'),
    )
    
    stage = models.ForeignKey(QuestionStage, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=True)
    choices = models.TextField(blank=True, help_text="For multiple choice, provide options separated by semicolons")
    order = models.IntegerField(default=0)
    allowed_file_types = models.CharField(max_length=100, blank=True, help_text="Allowed file types for uploads (e.g., 'pdf,jpg,png')")
    max_file_size = models.IntegerField(default=5, help_text="Maximum file size in MB (default: 5)")
    
    def __str__(self):
        return f"{self.stage.stage_number}.{self.order}: {self.question_text[:50]}"
        
    class Meta:
        # Ensure exactly 10 questions per stage
        constraints = [
            models.UniqueConstraint(fields=['stage', 'order'], name='unique_question_order')
        ]
        ordering = ['stage', 'order']


def get_upload_path(instance, filename):
    """Generate a unique path for uploaded files"""
    return f'uploads/user_{instance.user.id}/{instance.question.id}/{filename}'

class Answer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    file_upload = models.FileField(upload_to=get_upload_path, blank=True, null=True)
    
    class Meta:
        unique_together = ['user', 'question']
    
    def __str__(self):
        return f"Answer by {self.user.email} to {self.question.question_text[:30]}"
        
    def get_answer_display(self):
        """Get a formatted display of the answer based on question type"""
        if self.question.question_type == 'file' and self.file_upload:
            return f'<a href="{self.file_upload.url}" target="_blank">View Uploaded File</a>'
        elif self.question.question_type == 'dob' and self.answer_text:
            try:
                # Format as DD.MM.YYYY (German format)
                from datetime import datetime
                date_obj = datetime.strptime(self.answer_text, '%Y-%m-%d')
                return date_obj.strftime('%d.%m.%Y')
            except:
                return self.answer_text
        return self.answer_text


class ApplicationSource(models.Model):
    name = models.CharField(max_length=100)
    tracking_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class ApplicantTracking(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='tracking')
    source = models.ForeignKey(ApplicationSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='applicants')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Tracking for {self.user.email}"
