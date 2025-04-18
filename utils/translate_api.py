import os
import html
import json
import requests
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

# Google Translate API settings
API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY', '')
TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'

def translate_text(text, target_language=None, source_language=None):
    """
    Translate text using Google Cloud Translation API via REST API.
    
    Args:
        text (str): The text to translate
        target_language (str, optional): Target language code (e.g., 'de', 'en'). 
                                        If None, uses current Django language.
        source_language (str, optional): Source language code. If None, Google will auto-detect.
    
    Returns:
        str: Translated text
    """
    if not text or not isinstance(text, str):
        return text
        
    # If text is very short (like a single letter), don't translate
    if len(text.strip()) <= 1:
        return text
    
    # Skip translation if the text appears to be HTML, code or mostly numbers/symbols
    if '<' in text and '>' in text:  # Simple check for HTML
        return text
    
    # If target language not provided, use current Django language
    if not target_language:
        target_language = get_language()
        if target_language:
            # Django uses language codes like 'en-us', but Google uses 'en'
            target_language = target_language.split('-')[0]
    
    # Prepare data for API request
    data = {
        'q': text,
        'target': target_language,
        'key': API_KEY,
        'format': 'text'
    }
    
    # Add source language if provided
    if source_language:
        data['source'] = source_language
        
    try:
        # Make API request
        response = requests.post(TRANSLATE_URL, data=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse response
        result = response.json()
        translated_text = result['data']['translations'][0]['translatedText']
        
        # Unescape HTML entities if any
        translated_text = html.unescape(translated_text)
        
        return translated_text
    except Exception as e:
        # Log error but return original text to avoid breaking the site
        print(f"Translation error: {e}")
        return text
        
def batch_translate(texts, target_language=None, source_language=None):
    """
    Translate a batch of texts using Google Cloud Translation API via REST API.
    
    Args:
        texts (list): List of texts to translate
        target_language (str, optional): Target language code. If None, uses current Django language.
        source_language (str, optional): Source language code. If None, Google will auto-detect.
    
    Returns:
        list: List of translated texts
    """
    if not texts:
        return texts
    
    # Filter out empty or non-string values
    valid_texts = [t for t in texts if t and isinstance(t, str)]
    if not valid_texts:
        return texts
    
    # If target language not provided, use current Django language
    if not target_language:
        target_language = get_language()
        if target_language:
            # Django uses language codes like 'en-us', but Google uses 'en'
            target_language = target_language.split('-')[0]
    
    # Prepare data for API request
    data = {
        'q': valid_texts,
        'target': target_language,
        'key': API_KEY,
        'format': 'text'
    }
    
    # Add source language if provided
    if source_language:
        data['source'] = source_language
        
    try:
        # Make API request
        response = requests.post(TRANSLATE_URL, data=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse response
        result = response.json()
        translations = [t['translatedText'] for t in result['data']['translations']]
        
        # Unescape HTML entities if any
        translations = [html.unescape(t) for t in translations]
        
        # Create a map of original texts to translated texts
        translation_map = {orig: trans for orig, trans in zip(valid_texts, translations)}
        
        # Return translated texts in the same order as input
        return [translation_map.get(t, t) if t and isinstance(t, str) else t for t in texts]
    except Exception as e:
        # Log error but return original texts to avoid breaking the site
        print(f"Batch translation error: {e}")
        return texts