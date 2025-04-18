from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    google_sheet_updated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Store applicant data if collected during chat
    applicant_name = models.CharField(max_length=255, blank=True, null=True)
    applicant_email = models.EmailField(blank=True, null=True)
    applicant_phone = models.CharField(max_length=20, blank=True, null=True)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    driving_experience = models.CharField(max_length=100, blank=True, null=True)
    availability = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Chat Session: {self.session_id}"
    
    def update_google_sheet(self):
        """Update Google Sheet with applicant data"""
        from utils.google_sheets import append_application_data
        
        if self.google_sheet_updated or not self.applicant_email:
            return False
            
        data = {
            'timestamp': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'name': self.applicant_name,
            'email': self.applicant_email,
            'phone': self.applicant_phone,
            'vehicle_type': self.vehicle_type,
            'experience': self.driving_experience,
            'availability': self.availability,
            'chat_session_id': self.session_id
        }
        
        success = append_application_data(data)
        if success:
            self.google_sheet_updated = True
            self.save()
        return success

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