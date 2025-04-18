from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.conf import settings
import json
import os
import uuid

from .services import ChatbotService
from .models import ChatSession

@ensure_csrf_cookie
def chatbot_view(request):
    """Render the chatbot interface"""
    # Get or create a chat session for this user
    chatbot_service = ChatbotService()
    if request.user.is_authenticated:
        session = chatbot_service.get_or_create_session(request.user)
    else:
        # For anonymous users, try to get session from cookies
        session_id = request.COOKIES.get('chat_session_id')
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id)
            except ChatSession.DoesNotExist:
                session = chatbot_service.get_or_create_session()
        else:
            session = chatbot_service.get_or_create_session()
    
    # Get chat history
    messages = chatbot_service.get_chat_history(session)
    
    context = {
        'chat_session': session,
        'messages': messages,
    }
    
    response = render(request, 'chatbot/chat.html', context)
    
    # Set cookie for anonymous users
    if not request.user.is_authenticated:
        response.set_cookie('chat_session_id', session.session_id, max_age=3600*24*7)  # 7 days
    
    return response

@require_POST
def send_message_api(request):
    """API endpoint to send a message to the chatbot"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get the session
        chatbot_service = ChatbotService()
        if request.user.is_authenticated:
            session = chatbot_service.get_or_create_session(request.user)
        else:
            session_id = request.COOKIES.get('chat_session_id')
            try:
                session = ChatSession.objects.get(session_id=session_id)
            except (ChatSession.DoesNotExist, TypeError):
                return JsonResponse({'error': 'Invalid session'}, status=400)
        
        # Process the message
        result = chatbot_service.send_message(session, message)
        
        if result['success']:
            return JsonResponse({
                'user_message': {
                    'content': result['user_message'].content,
                    'timestamp': result['user_message'].timestamp.isoformat(),
                },
                'assistant_message': {
                    'content': result['assistant_message'].content,
                    'timestamp': result['assistant_message'].timestamp.isoformat(),
                }
            })
        else:
            return JsonResponse({
                'error': 'Failed to get response',
                'message': result['assistant_message'].content
            }, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        
@require_POST
def upload_document(request):
    """Handle document uploads for the chatbot"""
    if not request.FILES.get('document'):
        messages.error(request, 'Please select a document to upload')
        return redirect('chatbot:chat')
    
    document = request.FILES['document']
    
    # Check file extension
    if not document.name.endswith('.pdf'):
        messages.error(request, 'Only PDF files are supported')
        return redirect('chatbot:chat')
    
    # Create documents directory if it doesn't exist
    documents_dir = os.path.join(settings.BASE_DIR, 'documents')
    if not os.path.exists(documents_dir):
        os.makedirs(documents_dir)
    
    # Generate a unique filename to avoid collisions
    filename = f"{uuid.uuid4().hex}-{document.name}"
    file_path = os.path.join(documents_dir, filename)
    
    # Save the file
    with open(file_path, 'wb+') as destination:
        for chunk in document.chunks():
            destination.write(chunk)
    
    # Process documents to update vector store
    try:
        chatbot_service = ChatbotService()
        chatbot_service.document_processor.process_documents()
        messages.success(request, 'Document uploaded successfully. You can now ask questions about it.')
    except Exception as e:
        messages.error(request, f'Error processing document: {str(e)}')
    
    return redirect('chatbot:chat')