import os
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.documents_dir = os.path.join('documents')
        self.vector_store = None
        self.embeddings = None
        
        # Create documents directory if it doesn't exist
        if not os.path.exists(self.documents_dir):
            os.makedirs(self.documents_dir)
        
        # Initialize the embeddings using OpenAI
        try:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY
            )
        except Exception as e:
            logger.error(f"Error initializing OpenAI embeddings: {e}")
    
    def load_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def process_documents(self):
        """Process all PDF documents in the documents directory"""
        if not self.embeddings:
            logger.error("OpenAI embeddings not initialized")
            return "OpenAI embeddings not initialized"
        
        # Get all PDF files in the documents directory
        pdf_files = [f for f in os.listdir(self.documents_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            logger.info("No PDF documents found to process")
            return "No PDF documents found to process"
        
        # Process each PDF file
        documents_text = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.documents_dir, pdf_file)
            text = self.load_pdf(pdf_path)
            if text:
                documents_text.append(text)
        
        if not documents_text:
            logger.info("No text extracted from PDF documents")
            return "No text extracted from PDF documents"
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        chunks = []
        for text in documents_text:
            chunks.extend(text_splitter.split_text(text))
        
        # Create vector store from documents
        try:
            self.vector_store = FAISS.from_texts(chunks, self.embeddings)
            logger.info(f"Vector store created with {len(chunks)} chunks")
            return f"Vector store created with {len(chunks)} chunks"
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            return f"Error creating vector store: {e}"
    
    def query_documents(self, query, k=3):
        """Query the vector store for relevant document chunks"""
        if not self.vector_store:
            # If vector store is not initialized, try to process documents
            try:
                self.process_documents()
            except Exception as e:
                logger.error(f"Error processing documents: {e}")
                return ["No documents available to query."]
            
            # If still no vector store, return empty results
            if not self.vector_store:
                return ["No documents available to query."]
        
        try:
            # Get similar document chunks from the vector store
            docs = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return [f"Error querying knowledge base: {e}"]