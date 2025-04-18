from openai import OpenAI
import uuid
import re
from django.conf import settings
from .models import ChatSession, ChatMessage
from .document_processor import DocumentProcessor

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

class ChatbotService:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        # Pre-process documents if any
        try:
            self.document_processor.process_documents()
        except Exception as e:
            print(f"Error processing documents: {e}")
        
    def get_or_create_session(self, user=None):
        """Get existing session for user or create a new one"""
        if user and user.is_authenticated:
            # Try to find an existing session for this user
            session = ChatSession.objects.filter(user=user).order_by('-updated_at').first()
            if session:
                return session
        
        # Create a new session
        session_id = str(uuid.uuid4())
        session = ChatSession.objects.create(
            user=user if user and user.is_authenticated else None,
            session_id=session_id
        )
        
        # Add system message with context about the delivery driver recruitment
        system_message = (
            "You are a helpful assistant for a delivery driver recruitment platform. "
            "You can help answer questions about the application process, requirements, "
            "compensation, scheduling, and other related topics. Be friendly, professional, "
            "and encouraging. Your goal is to help potential drivers understand the benefits "
            "of joining our delivery team and guide them through the application process.\n\n"
            "IMPORTANT: If the user expresses interest in applying or provides personal information, "
            "extract and save their details. Ask for their name, email, phone number, "
            "vehicle type, driving experience, and availability if they don't provide this information."
        )
        
        ChatMessage.objects.create(
            session=session,
            role='system',
            content=system_message
        )
        
        return session
    
    def get_chat_history(self, session, limit=10):
        """Retrieve the chat history for a session"""
        return ChatMessage.objects.filter(session=session).order_by('timestamp')[:limit]
    
    def extract_applicant_info(self, session, message_text):
        """Extract applicant information from messages if provided"""
        
        # Check for email
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', message_text)
        if email_match and not session.applicant_email:
            session.applicant_email = email_match.group(0)
        
        # Check for phone number (simple pattern)
        phone_match = re.search(r'(\+\d{1,3}[-.\s]?)?(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\d{10})', message_text)
        if phone_match and not session.applicant_phone:
            session.applicant_phone = phone_match.group(0)
        
        # Look for name patterns (this is simplistic and might need improvement)
        name_patterns = [
            r"my name is ([A-Za-z\s]+)",
            r"I am ([A-Za-z\s]+)",
            r"I'm ([A-Za-z\s]+)",
            r"([A-Za-z\s]+) here"
        ]
        
        if not session.applicant_name:
            for pattern in name_patterns:
                name_match = re.search(pattern, message_text, re.IGNORECASE)
                if name_match:
                    potential_name = name_match.group(1).strip()
                    # Filter out common phrases that aren't names
                    non_names = ["interested", "applying", "looking", "available"]
                    if len(potential_name.split()) <= 3 and not any(word in potential_name.lower() for word in non_names):
                        session.applicant_name = potential_name
                        break
        
        # Check for vehicle information
        vehicle_types = ["car", "bike", "motorcycle", "scooter", "bicycle", "van", "truck"]
        if not session.vehicle_type:
            for vehicle in vehicle_types:
                if vehicle in message_text.lower():
                    session.vehicle_type = vehicle
                    break
        
        # Check for experience mentions
        experience_patterns = [
            r"(\d+)\s*years?\s*experience",
            r"(\d+)\s*years?\s*of\s*experience",
            r"experience\s*of\s*(\d+)\s*years?"
        ]
        
        if not session.driving_experience:
            for pattern in experience_patterns:
                exp_match = re.search(pattern, message_text, re.IGNORECASE)
                if exp_match:
                    session.driving_experience = f"{exp_match.group(1)} years"
                    break
        
        # Look for availability info
        availability_keywords = ["available", "availability", "schedule", "part-time", "full-time", "weekends", "weekdays"]
        
        if not session.availability:
            for keyword in availability_keywords:
                if keyword in message_text.lower():
                    # Extract the sentence containing the keyword
                    sentences = message_text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            session.availability = sentence.strip()
                            break
                    if session.availability:
                        break
        
        # Save the updated session
        session.save()
        
        # If we have enough applicant info, update Google Sheets
        if session.applicant_email and session.applicant_name and not session.google_sheet_updated:
            session.update_google_sheet()
    
    def send_message(self, session, message_text):
        """
        Send a user message and get the AI response
        """
        # Extract applicant info
        self.extract_applicant_info(session, message_text)
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=message_text
        )
        
        # Get all messages for this session to maintain context
        messages = []
        for msg in ChatMessage.objects.filter(session=session).order_by('timestamp'):
            messages.append({
                'role': msg.role,
                'content': msg.content
            })
        
        # Try to find document context if the message appears to be a question
        document_context = ""
        if any(q in message_text.lower() for q in ["what", "how", "when", "where", "why", "who", "can", "is", "are", "policy", "requirement"]):
            try:
                docs = self.document_processor.query_documents(message_text)
                if docs and docs[0] != "No documents available to query.":
                    document_context = "\n\nHere's some information from our documents that might help answer this question:\n" + "\n".join(docs)
            except Exception as e:
                print(f"Error querying documents: {e}")
        
        # If we have document context, add it to the message
        if document_context:
            messages.append({
                'role': 'system',
                'content': f"Please use the following information from our documents to help answer the user's question: {document_context}"
            })
        
        try:
            # Call OpenAI API with the new client
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            
            # Extract the assistant's response
            assistant_message_content = response.choices[0].message.content
            
            # Save assistant response
            assistant_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=assistant_message_content
            )
            
            return {
                'user_message': user_message,
                'assistant_message': assistant_message,
                'success': True
            }
        except Exception as e:
            # Handle errors
            error_message = f"Sorry, I'm having trouble responding right now. Error: {str(e)}"
            assistant_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=error_message
            )
            
            return {
                'user_message': user_message,
                'assistant_message': assistant_message,
                'success': False,
                'error': str(e)
            }