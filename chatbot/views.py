from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
import json
import os
import logging
from .services import ChatbotService

logger = logging.getLogger(__name__)
chatbot_service = ChatbotService()

def chatbot_view(request):
    """Render the chatbot interface"""
    # Get or create a chat session for this user
    session = chatbot_service.get_or_create_session(request.user)
    
    # Get chat history
    chat_history = chatbot_service.get_chat_history(session)
    
    context = {
        'chat_history': chat_history,
        'session_id': session.session_id,
    }
    
    return render(request, 'chatbot/chat.html', context)

@csrf_exempt
@require_POST
def send_message_api(request):
    """API endpoint to send a message to the chatbot"""
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        session_id = data.get('session_id', '')
        
        if not message_text:
            return JsonResponse({'error': 'Message text is required'}, status=400)
        
        # Get the session by ID
        try:
            from .models import ChatSession
            session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            # Create a new session if one doesn't exist
            session = chatbot_service.get_or_create_session(request.user if request.user.is_authenticated else None)
        
        # Send the message to the chatbot service
        response = chatbot_service.send_message(session, message_text)
        
        # Return the response
        return JsonResponse({
            'success': response['success'],
            'message': response['assistant_message'].content,
            'timestamp': response['assistant_message'].timestamp.isoformat(),
        })
    
    except Exception as e:
        logger.error(f"Error in send_message_api: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def upload_document(request):
    """Handle document uploads for the chatbot"""
    if 'document' not in request.FILES:
        return JsonResponse({'error': 'No document uploaded'}, status=400)
    
    document = request.FILES['document']
    
    # Check file extension
    if not document.name.lower().endswith('.pdf'):
        return JsonResponse({'error': 'Only PDF files are allowed'}, status=400)
    
    # Create documents directory if it doesn't exist
    documents_dir = os.path.join('documents')
    if not os.path.exists(documents_dir):
        os.makedirs(documents_dir)
    
    # Save the document
    document_path = os.path.join(documents_dir, document.name)
    try:
        with open(document_path, 'wb+') as destination:
            for chunk in document.chunks():
                destination.write(chunk)
    except Exception as e:
        logger.error(f"Error saving document: {e}")
        return JsonResponse({'error': f'Error saving document: {str(e)}'}, status=500)
    
    # Process the document
    try:
        result = chatbot_service.document_processor.process_documents()
        return JsonResponse({
            'success': True,
            'message': f'Document uploaded and processed successfully. {result}',
            'document_name': document.name
        })
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return JsonResponse({'error': f'Document uploaded but error during processing: {str(e)}'}, status=500)