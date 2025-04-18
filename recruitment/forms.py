from django import forms
from .models import Question, Answer


class BaseQuestionnaireForm(forms.Form):
    def __init__(self, stage, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        questions = Question.objects.filter(stage__stage_number=stage).order_by('order')
        
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
                choices = [(c.strip(), c.strip()) for c in question.choices.split(';')]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.question_text,
                    required=question.is_required,
                    choices=choices,
                    widget=forms.Select(attrs={'class': 'form-select'})
                )
            
            elif question.question_type == 'boolean':
                self.fields[field_name] = forms.BooleanField(
                    label=question.question_text,
                    required=False,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                )
            
            # Pre-fill with existing answer if available
            if self.user:
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
