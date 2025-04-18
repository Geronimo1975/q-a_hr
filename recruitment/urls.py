from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('questionnaire/<int:stage>/', views.questionnaire, name='questionnaire'),
    path('success/', views.success_view, name='success'),
    path('track/<str:tracking_code>/', views.track_source, name='track_source'),
]
