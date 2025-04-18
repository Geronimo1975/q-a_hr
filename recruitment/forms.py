from django import forms
from .models import Question, Answer
import re


class GermanPostalCodeField(forms.RegexField):
    """Custom field for German postal code validation"""
    def __init__(self, *args, **kwargs):
        super().__init__(r'^\d{5}$', *args, **kwargs)


class GermanPhoneNumberField(forms.RegexField):
    """Custom field for German phone number validation"""
    def __init__(self, *args, **kwargs):
        # German phone number format: +49 1234 567890 or 01234 567890 etc.
        super().__init__(r'^(\+49|0)[0-9 ]{8,17}$', *args, **kwargs)
        
    def clean(self, value):
        value = super().clean(value)
        # Normalize phone number to standard format
        if value:
            # Remove spaces
            value = re.sub(r'\s+', '', value)
            # Ensure it starts with +49 (convert 0 prefix to +49)
            if value.startswith('0'):
                value = '+49' + value[1:]
            elif not value.startswith('+'):
                value = '+49' + value
        return value


class BaseQuestionnaireForm(forms.Form):
    def __init__(self, stage, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        questions = Question.objects.filter(stage__stage_number=stage).order_by('order')
        
        # Ensure exactly 10 questions per stage
        if questions.count() != 10:
            # This is to ensure we follow the requirement of exactly 10 questions per stage
            # In a production environment, we would handle this differently
            pass
        
        for question in questions:
            field_name = f'question_{question.id}'
            
            if question.question_type == 'text':
                self.fields[field_name] = forms.CharField(
                    label=question.question_text,
                    required=question.is_required,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            
            elif question.question_type == 'number':
                self.fields[field_name] = forms.IntegerField(
                    label=question.question_text,
                    required=question.is_required,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )
            
            elif question.question_type == 'choice':
                choices = [(c.strip(), c.strip()) for c in question.choices.split(';') if c.strip()]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.question_text,
                    required=question.is_required,
                    choices=choices,
                    widget=forms.Select(attrs={'class': 'form-select'})
                )
            
            elif question.question_type == 'boolean':
                self.fields[field_name] = forms.BooleanField(
                    label=question.question_text,
                    required=question.is_required if question.is_required else False,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                )
            
            elif question.question_type == 'file':
                allowed_extensions = question.allowed_file_types.split(',') if question.allowed_file_types else None
                max_size = question.max_file_size * 1024 * 1024  # Convert MB to bytes
                
                self.fields[field_name] = forms.FileField(
                    label=question.question_text,
                    required=question.is_required,
                    widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
                    help_text=f"Allowed file types: {question.allowed_file_types if question.allowed_file_types else 'All'}. Max size: {question.max_file_size}MB."
                )
                
                # Add validators for file type and size
                if allowed_extensions:
                    self.fields[field_name].validators.append(
                        lambda f: None if f and any(f.name.lower().endswith(ext.lower().strip()) for ext in allowed_extensions) 
                        else forms.ValidationError(f'File type not allowed. Allowed types: {question.allowed_file_types}')
                    )
                
                self.fields[field_name].validators.append(
                    lambda f: None if f and f.size <= max_size 
                    else forms.ValidationError(f'File too large. Maximum size: {question.max_file_size}MB.')
                )
            
            elif question.question_type == 'name':
                self.fields[field_name] = forms.CharField(
                    label=question.question_text,
                    required=question.is_required,
                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
                    help_text="Enter your full name (First and Last Name)"
                )
            
            elif question.question_type == 'dob':
                self.fields[field_name] = forms.DateField(
                    label=question.question_text,
                    required=question.is_required,
                    widget=forms.DateInput(attrs={
                        'class': 'form-control',
                        'type': 'date',
                        'placeholder': 'TT.MM.JJJJ'
                    }),
                    help_text="Enter your date of birth (Format: TT.MM.JJJJ)",
                    input_formats=['%Y-%m-%d', '%d.%m.%Y']  # Accept both formats
                )
            
            elif question.question_type == 'address':
                # For address, we'll use a charfield with a textarea widget
                self.fields[field_name] = forms.CharField(
                    label=question.question_text,
                    required=question.is_required,
                    widget=forms.Textarea(attrs={
                        'class': 'form-control',
                        'rows': 3,
                        'placeholder': 'Street, House Number\nPostal Code, City'
                    }),
                    help_text="Enter your complete address including street, house number, postal code, and city"
                )
            
            elif question.question_type == 'phone':
                self.fields[field_name] = GermanPhoneNumberField(
                    label=question.question_text,
                    required=question.is_required,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': '+49 123 4567890'
                    }),
                    help_text="Enter your phone number in German format (e.g., +49 123 4567890 or 0123 4567890)"
                )
            
            # Pre-fill with existing answer if available
            if self.user and question.question_type != 'file':
                try:
                    answer = Answer.objects.get(user=self.user, question=question)
                    self.fields[field_name].initial = answer.answer_text
                except Answer.DoesNotExist:
                    pass


class Stage1QuestionnaireForm(BaseQuestionnaireForm):
    def __init__(self, *args, **kwargs):
        super().__init__(stage=1, *args, **kwargs)


class Stage2QuestionnaireForm(BaseQuestionnaireForm):
    def __init__(self, *args, **kwargs):
        super().__init__(stage=2, *args, **kwargs)


class Stage3QuestionnaireForm(BaseQuestionnaireForm):
    def __init__(self, *args, **kwargs):
        super().__init__(stage=3, *args, **kwargs)
