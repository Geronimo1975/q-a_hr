import os
from google.cloud import translate_v2 as translate
from django.conf import settings
from django.utils.translation import get_language

# Initialize the Google Translate client
translate_client = translate.Client(key=os.environ.get('GOOGLE_TRANSLATE_API_KEY'))

def translate_text(text, target_language=None, source_language=None):
    """
    Translate text using Google Cloud Translation API.
    
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
    
    try:
        # Perform translation
        result = translate_client.translate(
            text, 
            target_language=target_language,
            source_language=source_language,
            format_='text'  # Use 'html' if translating HTML content
        )
        return result['translatedText']
    except Exception as e:
        # Log error but return original text to avoid breaking the site
        print(f"Translation error: {e}")
        return text

def batch_translate(texts, target_language=None, source_language=None):
    """
    Translate a batch of texts using Google Cloud Translation API.
    
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
    
    try:
        results = translate_client.translate(
            valid_texts, 
            target_language=target_language,
            source_language=source_language,
            format_='text'
        )
        
        # Create a map of original texts to translated texts
        translations = {orig: result['translatedText'] 
                      for orig, result in zip(valid_texts, results)}
        
        # Return translated texts in the same order as input
        return [translations.get(t, t) if t and isinstance(t, str) else t for t in texts]
    except Exception as e:
        # Log error but return original texts to avoid breaking the site
        print(f"Batch translation error: {e}")
        return texts