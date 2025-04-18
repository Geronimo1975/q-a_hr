from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chat'),
    path('api/send-message/', views.send_message_api, name='send_message_api'),
    path('upload-document/', views.upload_document, name='upload_document'),
]