from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('send/', views.send_message_api, name='send_message'),
    path('upload/', views.upload_document, name='upload_document'),
    path('admin/documents/', views.admin_document_list, name='admin_documents'),
    path('admin/fine-tuning/', views.fine_tuning_dashboard, name='fine_tuning'),
]