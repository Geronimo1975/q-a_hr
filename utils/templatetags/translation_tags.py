from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, gettext as _
from django.conf import settings
import logging

# Create a logger instance
logger = logging.getLogger(__name__)

register = template.Library()

@register.filter(name='direct_translate')
def direct_translate_filter(value, target_language=None):
    """
    A template filter that provides on-the-fly translation without needing the Google API.
    This is a simple dictionary-based translation system.
    
    Usage: {{ "Text to translate"|direct_translate }}
    Or with target language: {{ "Text to translate"|direct_translate:"de" }}
    """
    if not value:
        return value
    
    # If no target language specified, use current Django language
    if not target_language:
        target_language = get_language()
        if target_language:
            # Django uses language codes like 'en-us', but Google uses 'en'
            target_language = target_language.split('-')[0]
    
    # Skip translation for German (our base language)
    if target_language == 'de':
        return value
    
    # Log that we're doing translation
    logger.info(f"Direct translate filter: '{value}' to {target_language}")
    
    # Use built-in Django translation first
    translated_by_django = _(value)
    if translated_by_django != value:
        logger.info(f"Django translated: '{value}' -> '{translated_by_django}'")
        return mark_safe(translated_by_django)
    
    # A very simple dictionary of common phrases in multiple languages
    # This is fallback for when Google Translate API is not available
    translations = {
        'en': {
            'Home': 'Home',
            'Dashboard': 'Dashboard',
            'Profile': 'Profile',
            'Sign In': 'Sign In',
            'Sign Up': 'Sign Up',
            'Log Out': 'Log Out',
            'Apply Now': 'Apply Now',
            'Chat with Us': 'Chat with Us',
            'Become a Delivery Driver': 'Become a Delivery Driver',
            'Flexible Schedule': 'Flexible Schedule',
            'Competitive Pay': 'Competitive Pay',
            'Benefits': 'Benefits',
            'Join Our Team': 'Join Our Team',
            'How It Works': 'How It Works',
            'Submit Application': 'Submit Application',
            'Interview Process': 'Interview Process',
            'Start Delivering': 'Start Delivering',
            'Testimonials': 'Testimonials',
            'Frequently Asked Questions': 'Frequently Asked Questions',
        },
        'pl': {
            'Home': 'Strona główna',
            'Dashboard': 'Panel',
            'Profile': 'Profil',
            'Sign In': 'Zaloguj się',
            'Sign Up': 'Zarejestruj się',
            'Log Out': 'Wyloguj się',
            'Apply Now': 'Aplikuj teraz',
            'Chat with Us': 'Porozmawiaj z nami',
            'Become a Delivery Driver': 'Zostań kierowcą dostawczym',
            'Flexible Schedule': 'Elastyczny harmonogram',
            'Competitive Pay': 'Konkurencyjne wynagrodzenie',
            'Benefits': 'Korzyści',
            'Join Our Team': 'Dołącz do naszego zespołu',
            'How It Works': 'Jak to działa',
            'Submit Application': 'Złóż aplikację',
            'Interview Process': 'Proces rekrutacyjny',
            'Start Delivering': 'Rozpocznij dostawy',
            'Testimonials': 'Opinie',
            'Frequently Asked Questions': 'Często zadawane pytania',
        },
        'ro': {
            'Home': 'Acasă',
            'Dashboard': 'Panou de control',
            'Profile': 'Profil',
            'Sign In': 'Conectare',
            'Sign Up': 'Înregistrare',
            'Log Out': 'Deconectare',
            'Apply Now': 'Aplică acum',
            'Chat with Us': 'Discută cu noi',
            'Become a Delivery Driver': 'Devino șofer de livrare',
            'Flexible Schedule': 'Program flexibil',
            'Competitive Pay': 'Remunerație competitivă',
            'Benefits': 'Beneficii',
            'Join Our Team': 'Alătură-te echipei noastre',
            'How It Works': 'Cum funcționează',
            'Submit Application': 'Trimite aplicația',
            'Interview Process': 'Procesul de interviu',
            'Start Delivering': 'Începe livrările',
            'Testimonials': 'Mărturii',
            'Frequently Asked Questions': 'Întrebări frecvente',
        },
        'uk': {
            'Home': 'Головна',
            'Dashboard': 'Панель керування',
            'Profile': 'Профіль',
            'Sign In': 'Увійти',
            'Sign Up': 'Зареєструватися',
            'Log Out': 'Вийти',
            'Apply Now': 'Подати заявку',
            'Chat with Us': 'Поспілкуйтеся з нами',
            'Become a Delivery Driver': 'Станьте водієм доставки',
            'Flexible Schedule': 'Гнучкий графік',
            'Competitive Pay': 'Конкурентна зарплата',
            'Benefits': 'Переваги',
            'Join Our Team': 'Приєднуйтесь до нашої команди',
            'How It Works': 'Як це працює',
            'Submit Application': 'Подати заявку',
            'Interview Process': 'Процес співбесіди',
            'Start Delivering': 'Почати доставку',
            'Testimonials': 'Відгуки',
            'Frequently Asked Questions': 'Поширені запитання',
        },
        'ar': {
            'Home': 'الرئيسية',
            'Dashboard': 'لوحة التحكم',
            'Profile': 'الملف الشخصي',
            'Sign In': 'تسجيل الدخول',
            'Sign Up': 'التسجيل',
            'Log Out': 'تسجيل الخروج',
            'Apply Now': 'تقدم الآن',
            'Chat with Us': 'تحدث معنا',
            'Become a Delivery Driver': 'كن سائق توصيل',
            'Flexible Schedule': 'جدول مرن',
            'Competitive Pay': 'أجر تنافسي',
            'Benefits': 'المزايا',
            'Join Our Team': 'انضم إلى فريقنا',
            'How It Works': 'كيف يعمل',
            'Submit Application': 'قدم طلبك',
            'Interview Process': 'عملية المقابلة',
            'Start Delivering': 'ابدأ التوصيل',
            'Testimonials': 'الشهادات',
            'Frequently Asked Questions': 'الأسئلة الشائعة',
        },
        'tr': {
            'Home': 'Ana Sayfa',
            'Dashboard': 'Kontrol Paneli',
            'Profile': 'Profil',
            'Sign In': 'Giriş Yap',
            'Sign Up': 'Kayıt Ol',
            'Log Out': 'Çıkış Yap',
            'Apply Now': 'Şimdi Başvur',
            'Chat with Us': 'Bizimle Sohbet Et',
            'Become a Delivery Driver': 'Kurye Ol',
            'Flexible Schedule': 'Esnek Program',
            'Competitive Pay': 'Rekabetçi Ücret',
            'Benefits': 'Avantajlar',
            'Join Our Team': 'Ekibimize Katıl',
            'How It Works': 'Nasıl Çalışır',
            'Submit Application': 'Başvuruyu Gönder',
            'Interview Process': 'Mülakat Süreci',
            'Start Delivering': 'Teslimat Yapmaya Başla',
            'Testimonials': 'Kullanıcı Yorumları',
            'Frequently Asked Questions': 'Sık Sorulan Sorular',
        },
    }
    
    # Look up the translation in our dictionary
    if target_language in translations and value in translations[target_language]:
        translated_text = translations[target_language][value]
        logger.info(f"Dictionary translated: '{value}' -> '{translated_text}'")
        return mark_safe(translated_text)
    
    # Fall back to the original text if no translation found
    logger.info(f"No translation found for: '{value}' to {target_language}")
    return value

@register.simple_tag(name='direct_translate')
def direct_translate_tag(text, target_language=None):
    """
    A template tag for direct translations without requiring Google API.
    
    Usage: {% direct_translate "Text to translate" %}
    Or with target language: {% direct_translate "Text to translate" "de" %}
    """
    # Use the same implementation as the filter
    return direct_translate_filter(text, target_language)