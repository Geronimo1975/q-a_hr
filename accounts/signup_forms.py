from django import forms
from allauth.account.forms import SignupForm


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
        
        # Track application source if available
        from recruitment.models import ApplicationSource, ApplicantTracking
        source_id = request.session.get('application_source_id')
        if source_id:
            try:
                source = ApplicationSource.objects.get(id=source_id)
                ApplicantTracking.objects.create(user=user, source=source)
                # Clear from session after use
                del request.session['application_source_id']
            except ApplicationSource.DoesNotExist:
                pass
                
        return user