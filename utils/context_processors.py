from utils.translate_api import translate_text

def translation_context(request):
    """
    Context processor to make translation functions available to all templates.
    """
    return {
        'translate_text': translate_text,
    }