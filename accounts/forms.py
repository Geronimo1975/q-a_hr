from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    gdpr_consent = forms.BooleanField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'gdpr_consent', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number')


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    phone_number = forms.CharField(max_length=20, label='Phone Number')
    gdpr_consent = forms.BooleanField(
        required=True,
        label='I consent to the processing of my personal data',
        help_text='By checking this box, you acknowledge that you have read and understood our Privacy Policy and agree to the collection, use, and processing of your personal data as described therein. We will use your data only for the recruitment process and will not share it with third parties without your consent. You have the right to access, correct, or delete your personal data at any time by contacting us.'
    )
    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.gdpr_consent = self.cleaned_data['gdpr_consent']
        user.save()
        return user
