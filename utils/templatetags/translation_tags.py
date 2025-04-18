from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from utils.translate_api import translate_text

register = template.Library()

@register.filter(name='translate')
def translate_filter(value, target_language=None):
    """
    A template filter that translates text using Google Translate API.
    Usage: {{ "Text to translate"|translate }}
    Or with target language: {{ "Text to translate"|translate:"de" }}
    """
    if not value:
        return value
    
    # If no target language specified, use current Django language
    if not target_language:
        target_language = get_language()
        if target_language:
            # Django uses language codes like 'en-us', but Google uses 'en'
            target_language = target_language.split('-')[0]
    
    translated_text = translate_text(value, target_language=target_language)
    return mark_safe(translated_text)

@register.simple_tag(name='translate')
def translate_tag(text, target_language=None, source_language=None):
    """
    A template tag that translates text using Google Translate API.
    Usage: {% translate "Text to translate" %}
    Or with target language: {% translate "Text to translate" "de" %}
    Or with source and target: {% translate "Text to translate" "de" "en" %}
    """
    if not text:
        return text
    
    # If no target language specified, use current Django language
    if not target_language:
        target_language = get_language()
        if target_language:
            # Django uses language codes like 'en-us', but Google uses 'en'
            target_language = target_language.split('-')[0]
    
    translated_text = translate_text(
        text, 
        target_language=target_language,
        source_language=source_language
    )
    return mark_safe(translated_text)