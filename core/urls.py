from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('source/<str:tracking_code>/', views.track_source, name='track_source'),
    
    # Legal pages
    path('impressum/', views.impressum_view, name='impressum'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms/', views.terms_view, name='terms'),
    path('cookie-policy/', views.cookie_policy_view, name='cookie_policy'),
]
