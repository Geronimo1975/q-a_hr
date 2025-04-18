import os
import uuid
import json
import re
from datetime import datetime
from django.conf import settings
from openai import OpenAI
from .models import ChatSession, ChatMessage
from .document_processor import DocumentProcessor

class ChatbotService:
    def __init__(self):
        """Initialize the chatbot service with necessary components"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"  # Default model
        self.document_processor = DocumentProcessor()
        
        # Check if we have a fine-tuned model set
        if hasattr(settings, 'OPENAI_FINE_TUNED_MODEL') and settings.OPENAI_FINE_TUNED_MODEL:
            self.model = settings.OPENAI_FINE_TUNED_MODEL
    
    def get_or_create_session(self, user=None):
        """Get existing session for user or create a new one"""
        if user and user.is_authenticated:
            # Try to find an existing session for the user
            session = ChatSession.objects.filter(user=user).order_by('-created_at').first()
            if session:
                return session
        
        # Create a new session
        session_id = str(uuid.uuid4())
        session = ChatSession.objects.create(
            user=user if user and user.is_authenticated else None,
            session_id=session_id
        )
        
        # Add initial system message
        ChatMessage.objects.create(
            session=session,
            role="system",
            content=(
                "You are a helpful assistant for the Delivery Driver Recruitment Portal. "
                "Your goal is to assist potential delivery driver applicants by answering "
                "their questions about the application process, requirements, compensation, "
                "and other related topics. Be friendly, professional, and concise."
            )
        )
        
        return session
    
    def get_chat_history(self, session, limit=10):
        """Retrieve the chat history for a session"""
        return ChatMessage.objects.filter(session=session).order_by('timestamp')[:limit]
    
    def extract_applicant_info(self, session, message_text):
        """Extract applicant information from messages if provided"""
        # Only extract if we don't already have this info
        if not session.applicant_name or not session.applicant_email:
            # Check for email
            email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', message_text)
            if email_match and not session.applicant_email:
                session.applicant_email = email_match.group(0)
            
            # Check for name patterns
            name_patterns = [
                r'my name is ([A-Z][a-z]+ [A-Z][a-z]+)',
                r'I am ([A-Z][a-z]+ [A-Z][a-z]+)',
                r'I\'m ([A-Z][a-z]+ [A-Z][a-z]+)'
            ]
            
            for pattern in name_patterns:
                name_match = re.search(pattern, message_text)
                if name_match and not session.applicant_name:
                    session.applicant_name = name_match.group(1)
            
            # Check for phone number
            phone_match = re.search(r'\b\+?[\d\s\(\)-]{10,15}\b', message_text)
            if phone_match and not session.applicant_phone:
                session.applicant_phone = phone_match.group(0)
                
            # If we extracted any information, save the session
            if session.applicant_name or session.applicant_email or session.applicant_phone:
                session.save()
    
    def send_message(self, session, message_text):
        """
        Send a user message and get the AI response
        """
        # Store the user message
        ChatMessage.objects.create(
            session=session,
            role="user",
            content=message_text
        )
        
        # Extract any applicant information from the message
        self.extract_applicant_info(session, message_text)
        
        # Get context from relevant documents
        document_context = ""
        relevant_docs = self.document_processor.query_documents(message_text, k=2)
        if relevant_docs:
            document_context = "Information from relevant documents:\n"
            for doc in relevant_docs:
                document_context += f"- {doc['content']}\n\n"
        
        # Build message history for the API call
        messages = []
        
        # Add system message
        system_message = ChatMessage.objects.filter(session=session, role="system").first()
        if system_message:
            messages.append({"role": "system", "content": system_message.content})
            
            # If we have document context, append it to the system message
            if document_context:
                messages[0]["content"] += f"\n\n{document_context}"
        
        # Add conversation history (last 10 messages)
        history = ChatMessage.objects.filter(
            session=session, 
            role__in=["user", "assistant"]
        ).order_by('timestamp')
        
        # Skip the most recent user message (we'll add it separately)
        for msg in history[:-1]:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add the current user message
        messages.append({"role": "user", "content": message_text})
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            # Extract the assistant's message
            assistant_message = response.choices[0].message.content
            
            # Store the assistant message
            ChatMessage.objects.create(
                session=session,
                role="assistant",
                content=assistant_message
            )
            
            return assistant_message
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            # Store error message
            error_msg = f"I'm sorry, I encountered an error: {str(e)}"
            ChatMessage.objects.create(
                session=session,
                role="assistant",
                content=error_msg
            )
            return error_msg