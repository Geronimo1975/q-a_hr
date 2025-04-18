import os
import re
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from django.conf import settings

class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor with necessary components"""
        self.documents_dir = os.path.join(settings.MEDIA_ROOT, 'training_documents')
        self.vector_store_path = os.path.join(settings.MEDIA_ROOT, 'vector_store')
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.vector_store = None
        
        # Create directories if they don't exist
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(self.vector_store_path, exist_ok=True)
        
        # Try to load existing vector store
        try:
            if os.path.exists(os.path.join(self.vector_store_path, 'index.faiss')):
                self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings)
        except Exception as e:
            print(f"Error loading vector store: {e}")
    
    def load_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def process_documents(self):
        """Process all PDF documents in the documents directory"""
        all_docs = []
        for filename in os.listdir(self.documents_dir):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(self.documents_dir, filename)
                print(f"Processing {file_path}...")
                
                # Extract text from PDF
                text = self.load_pdf(file_path)
                if text:
                    # Split text into chunks
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1000,
                        chunk_overlap=200,
                        separators=["\n\n", "\n", ". ", " ", ""]
                    )
                    chunks = text_splitter.split_text(text)
                    
                    # Add metadata to chunks
                    docs = [
                        {"content": chunk, "metadata": {"source": filename}} 
                        for chunk in chunks
                    ]
                    all_docs.extend(docs)
        
        # Create or update the vector store
        if all_docs:
            if self.vector_store:
                # Add new documents to existing store
                self.vector_store.add_documents(all_docs)
            else:
                # Create new vector store
                self.vector_store = FAISS.from_documents(all_docs, self.embeddings)
            
            # Save the vector store
            self.vector_store.save_local(self.vector_store_path)
            return len(all_docs)
        
        return 0
    
    def extract_qa_pairs(self, text):
        """Extract question-answer pairs from a FAQ document"""
        # Simple pattern matching for Q&A format
        qa_pattern = r'(?:Q|Question)[:\.]?\s*(.*?)\s*(?:A|Answer)[:\.]?\s*(.*?)(?=(?:Q|Question)[:\.]?|\Z)'
        matches = re.finditer(qa_pattern, text, re.DOTALL | re.IGNORECASE)
        
        qa_pairs = []
        for match in matches:
            question = match.group(1).strip()
            answer = match.group(2).strip()
            if question and answer:
                qa_pairs.append((question, answer))
        
        return qa_pairs
    
    def extract_policy_statements(self, text):
        """Extract policy statements from a policy document"""
        # Split by sections
        sections = re.split(r'\n\s*\n|\r\n\s*\r\n', text)
        
        policy_statements = []
        current_topic = "General Policy"
        
        for section in sections:
            # Check if this is a heading
            if re.match(r'^[A-Z][\w\s]{2,50}$', section.strip()):
                current_topic = section.strip()
            elif len(section.strip()) > 50:  # Minimum content length
                policy_statements.append({"topic": current_topic, "content": section.strip()})
        
        return policy_statements
    
    def query_documents(self, query, k=3):
        """Query the vector store for relevant document chunks"""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "Unknown")
                }
                for doc in results
            ]
        except Exception as e:
            print(f"Error querying documents: {e}")
            return []