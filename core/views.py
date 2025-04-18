from django.shortcuts import render, redirect
from django.http import Http404
from recruitment.models import ApplicationSource, ApplicantTracking


def home_view(request):
    return render(request, 'home.html')


def track_source(request, tracking_code=None):
    """Track the source of an application based on a tracking code."""
    try:
        source = ApplicationSource.objects.get(tracking_code=tracking_code)
        # Store the source in the session for later use during registration
        request.session['application_source_id'] = source.id
    except ApplicationSource.DoesNotExist:
        pass
    
    # Redirect to the homepage or registration page
    return redirect('home')
