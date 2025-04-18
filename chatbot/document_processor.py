import os
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from django.conf import settings

class DocumentProcessor:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.docs_dir = os.path.join(settings.BASE_DIR, 'documents')
        self.vector_store = None
        
    def load_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
            
    def process_documents(self):
        """Process all PDF documents in the documents directory"""
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)
            
        documents = []
        for filename in os.listdir(self.docs_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(self.docs_dir, filename)
                text = self.load_pdf(file_path)
                documents.append(text)
                
        if not documents:
            return False
            
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        chunks = []
        for doc in documents:
            chunks.extend(text_splitter.split_text(doc))
            
        # Create vector store
        self.vector_store = FAISS.from_texts(chunks, self.embeddings)
        return True
        
    def query_documents(self, query, k=3):
        """Query the vector store for relevant document chunks"""
        if not self.vector_store:
            if not self.process_documents():
                return ["No documents available to query."]
                
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]