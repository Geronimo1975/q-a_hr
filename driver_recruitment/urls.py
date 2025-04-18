from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

# Non-translatable URLs
urlpatterns = [
    path('admin/', admin.site.urls),  # Keep admin outside i18n patterns
    path('i18n/', include('django.conf.urls.i18n')),  # For language switching
]

# Translatable URLs - will be prefixed with language code
urlpatterns += i18n_patterns(
    path(_('accounts/'), include('allauth.urls')),
    path(_('accounts/'), include('accounts.urls')),
    path(_('recruitment/'), include('recruitment.urls')),
    path(_('chat/'), include('chatbot.urls', namespace='chatbot')),
    path('', include('core.urls')),
    prefix_default_language=True  # Always include language code in URL
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
