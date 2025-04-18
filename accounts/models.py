from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True)
    gdpr_consent = models.BooleanField(default=False)
    application_stage = models.IntegerField(default=0)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_stage_status(self):
        if self.is_rejected:
            return "Rejected"
        elif self.application_stage == 0:
            return "Registration Complete"
        elif self.application_stage == 1:
            return "Stage 1 Complete"
        elif self.application_stage == 2:
            return "Stage 2 Complete"
        elif self.application_stage == 3:
            return "Application Complete"
        else:
            return "Unknown"
