from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden
from .forms import Stage1QuestionnaireForm, Stage2QuestionnaireForm, Stage3QuestionnaireForm
from .models import Answer, Question, QuestionStage, ApplicationSource, ApplicantTracking
from accounts.models import CustomUser
from utils.google_sheets import update_sheet_with_answers
from utils.sheets_direct import update_sheet_with_answers as update_sheet_direct
from utils.google_sheets_service import update_sheet_with_answers as update_sheet_service


@login_required
def questionnaire(request, stage=1):
    user = request.user
    
    # Check if user is allowed to access this stage
    if user.application_stage < stage - 1 or user.is_rejected:
        messages.error(request, "You cannot access this stage yet or your application has been rejected.")
        return redirect('dashboard')
    
    # Check if user has already completed this stage
    if user.application_stage >= stage:
        messages.warning(request, f"You have already completed Stage {stage}.")
        return redirect('dashboard')
    
    # Determine which form to use
    form_classes = {
        1: Stage1QuestionnaireForm,
        2: Stage2QuestionnaireForm,
        3: Stage3QuestionnaireForm,
    }
    
    FormClass = form_classes.get(stage)
    
    if request.method == 'POST':
        form = FormClass(user=user, data=request.POST, files=request.FILES)
        
        if form.is_valid():
            # Save answers
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('question_'):
                    question_id = int(field_name.split('_')[1])
                    question = Question.objects.get(id=question_id)
                    
                    # Handle different question types
                    if question.question_type == 'file':
                        # Handle file uploads
                        file_upload = request.FILES.get(field_name)
                        if file_upload:
                            # Create or update answer with file
                            answer, created = Answer.objects.update_or_create(
                                user=user,
                                question=question,
                                defaults={
                                    'answer_text': file_upload.name,  # Store filename in text field
                                    'file_upload': file_upload  # Store actual file
                                }
                            )
                    elif question.question_type == 'dob':
                        # Format date as ISO for storage
                        if value:
                            try:
                                # Format for database storage (ISO format)
                                formatted_value = value.isoformat() if hasattr(value, 'isoformat') else str(value)
                                answer, created = Answer.objects.update_or_create(
                                    user=user,
                                    question=question,
                                    defaults={'answer_text': formatted_value}
                                )
                            except Exception as e:
                                messages.error(request, f"Error saving date of birth: {e}")
                    else:
                        # Handle all other question types
                        answer, created = Answer.objects.update_or_create(
                            user=user,
                            question=question,
                            defaults={'answer_text': str(value) if value is not None else ''}
                        )
            
            # Update user's application stage
            user.application_stage = stage
            user.save()
            
            # Save answers to Google Sheets if enabled
            if settings.GOOGLE_SHEETS.get('enabled', False):
                sheet_id = settings.GOOGLE_SHEETS.get('spreadsheet_id')
                if sheet_id:
                    # Use the standard Google Sheets method
                    try:
                        from utils.google_sheets import update_sheet_with_answers
                        sheets_updated = update_sheet_with_answers(user, stage, sheet_id)
                            
                        if not sheets_updated:
                            messages.warning(request, "Responses were saved locally but could not be exported to Google Sheets.")
                    except Exception as e:
                        print(f"Error exporting to Google Sheets: {e}")
                        messages.warning(request, "Responses were saved locally but could not be exported to Google Sheets.")
            
            # Send email notification
            if stage < 3:
                # Simulate acceptance to next stage (in a real system, you'd have logic here)
                # For demo purposes, we'll automatically progress users to the next stage
                acceptance = True
                
                if acceptance:
                    send_mail(
                        f'Your application has been accepted to Stage {stage+1}',
                        f'Congratulations! You have successfully completed Stage {stage} and are invited to continue to Stage {stage+1}.',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    messages.success(request, f"Stage {stage} completed successfully! You've been advanced to Stage {stage+1}.")
                else:
                    user.is_rejected = True
                    user.save()
                    send_mail(
                        'Application Status Update',
                        f'Thank you for your interest. We regret to inform you that your application will not proceed to the next stage.',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    messages.warning(request, "Thank you for your interest. Your application will not proceed to the next stage.")
            else:
                # Final stage completion
                send_mail(
                    'Application Successfully Completed',
                    'Thank you for completing all stages of the application. Our team will review your information and contact you soon.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, "Congratulations! You have successfully completed all stages of the application.")
            
            return redirect('dashboard')
    else:
        form = FormClass(user=user)
    
    try:
        stage_name = QuestionStage.objects.get(stage_number=stage).stage_name
    except QuestionStage.DoesNotExist:
        stage_name = f"Stage {stage}"
    
    return render(request, 'recruitment/questionnaire.html', {
        'form': form,
        'stage': stage,
        'stage_name': stage_name
    })


@login_required
def dashboard(request):
    user = request.user
    
    # Get answers for this user
    answers = Answer.objects.filter(user=user).order_by('question__stage__stage_number', 'question__order')
    
    # Get next stage information
    next_stage = user.application_stage + 1 if user.application_stage < 3 and not user.is_rejected else None
    
    try:
        if next_stage:
            next_stage_name = QuestionStage.objects.get(stage_number=next_stage).stage_name
        else:
            next_stage_name = None
    except QuestionStage.DoesNotExist:
        next_stage_name = f"Stage {next_stage}" if next_stage else None
    
    return render(request, 'recruitment/dashboard.html', {
        'user': user,
        'answers': answers,
        'next_stage': next_stage,
        'next_stage_name': next_stage_name
    })


@login_required
def success_view(request):
    return render(request, 'recruitment/success.html')
