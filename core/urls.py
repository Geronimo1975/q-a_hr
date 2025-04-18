from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('source/<str:tracking_code>/', views.track_source, name='track_source'),
]
