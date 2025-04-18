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
    )
    
    stage = models.ForeignKey(QuestionStage, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=True)
    choices = models.TextField(blank=True, help_text="For multiple choice, provide options separated by semicolons")
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.stage.stage_number}.{self.order}: {self.question_text[:50]}"


class Answer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'question']
    
    def __str__(self):
        return f"Answer by {self.user.email} to {self.question.question_text[:30]}"


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
