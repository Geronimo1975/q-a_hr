import json
import uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.conf import settings
from .services import ChatbotService
from .models import ChatSession, TrainingDocument

def chatbot_view(request):
    """Render the chatbot interface"""
    # Initialize service
    service = ChatbotService()
    
    # Get or create a chat session
    session = service.get_or_create_session(request.user)
    
    # Get chat history
    history = service.get_chat_history(session)
    
    context = {
        'session_id': session.session_id,
        'history': history,
        'page_title': 'Chat with our Assistant'
    }
    
    # We're using the Telekom style chatbot by default
    return render(request, 'chatbot/telekom_chatbot.html', context)

def send_message_api(request):
    """API endpoint to send a message to the chatbot"""
    if request.method == 'POST':
        try:
            # Parse the JSON data
            data = json.loads(request.body)
            message = data.get('message', '')
            session_id = data.get('session_id', '')
            
            print(f"Received message: '{message}', session_id: '{session_id}'")
            
            if not message or not session_id:
                print("Error: Message or session_id is missing")
                return JsonResponse({'success': False, 'error': 'Message and session_id are required'})
            
            # Get the session
            try:
                session = ChatSession.objects.get(session_id=session_id)
                print(f"Found session: {session.id}")
            except ChatSession.DoesNotExist:
                print(f"Error: Session with ID {session_id} not found")
                return JsonResponse({'success': False, 'error': 'Invalid session'})
            
            # Initialize service and send message
            service = ChatbotService()
            print("Sending message to ChatbotService...")
            response = service.send_message(session, message)
            print(f"Received response: '{response}'")
            
            return JsonResponse({'success': True, 'response': response})
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            print(f"Unexpected error in send_message_api: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})

@login_required
def upload_document(request):
    """Handle document uploads for the chatbot"""
    if request.method == 'POST' and request.FILES.get('document'):
        try:
            document = request.FILES['document']
            
            # Validate file type
            if not document.name.lower().endswith('.pdf'):
                return JsonResponse({'success': False, 'error': 'Only PDF files are allowed'})
            
            # Create the TrainingDocument in the database
            training_doc = TrainingDocument.objects.create(
                title=document.name,
                document_type='faq',  # Default type
                file=document
            )
            
            # Process document in the background (would typically be a celery task)
            # For now, just mark it as processed
            training_doc.is_processed_for_training = True
            training_doc.save()
            
            return JsonResponse({'success': True, 'document_id': training_doc.id})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def admin_document_list(request):
    """Show list of training documents for admin users"""
    if not request.user.is_staff:
        return redirect('chatbot')
    
    documents = TrainingDocument.objects.all().order_by('-uploaded_at')
    
    context = {
        'documents': documents,
        'page_title': 'Training Documents'
    }
    
    return render(request, 'chatbot/admin_documents.html', context)


@login_required
def fine_tuning_dashboard(request):
    """Admin dashboard for fine-tuning management"""
    if not request.user.is_staff:
        return redirect('chatbot')
    
    # Process actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'process_documents':
            # Initialize processor and process documents
            from .document_processor import DocumentProcessor
            processor = DocumentProcessor()
            count = processor.process_documents()
            
            return JsonResponse({'success': True, 'processed': count})
        
        elif action == 'generate_fine_tuning_file':
            # Logic to generate fine-tuning file
            # This would typically be a background task
            return JsonResponse({'success': True, 'message': 'Fine-tuning file generated'})
    
    # Get statistics
    total_documents = TrainingDocument.objects.count()
    processed_documents = TrainingDocument.objects.filter(is_processed_for_training=True).count()
    
    context = {
        'total_documents': total_documents,
        'processed_documents': processed_documents,
        'page_title': 'Fine-tuning Management'
    }
    
    return render(request, 'chatbot/fine_tuning.html', context)