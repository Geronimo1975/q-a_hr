import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')
django.setup()

from core.models import EditableContent

# Define initial content
content_items = [
    {
        'identifier': 'hero_title',
        'content_de': 'Werde Lieferfahrer',
        'content_en': 'Become a Delivery Driver',
        'content_pl': 'Zostań kierowcą dostawczym',
        'content_ro': 'Devino șofer de livrare',
        'content_uk': 'Станьте водієм доставки',
        'content_ar': 'كن سائق توصيل',
        'content_tr': 'Kurye Ol',
    },
    {
        'identifier': 'hero_subtitle',
        'content_de': 'Werde Teil unseres Teams professioneller Fahrer und genieße flexible Arbeitszeiten, wettbewerbsfähige Bezahlung und ein unterstützendes Arbeitsumfeld.',
        'content_en': 'Join our team of professional drivers and enjoy flexible hours, competitive pay, and a supportive work environment.',
        'content_pl': 'Dołącz do naszego zespołu profesjonalnych kierowców i ciesz się elastycznymi godzinami, konkurencyjnym wynagrodzeniem i wspierającym środowiskiem pracy.',
        'content_ro': 'Alătură-te echipei noastre de șoferi profesioniști și bucură-te de program flexibil, plată competitivă și un mediu de lucru suportiv.',
        'content_uk': 'Приєднуйтесь до нашої команди професійних водіїв та насолоджуйтесь гнучким графіком, конкурентною оплатою та підтримуючим робочим середовищем.',
        'content_ar': 'انضم إلى فريقنا من السائقين المحترفين واستمتع بساعات عمل مرنة وأجر تنافسي وبيئة عمل داعمة.',
        'content_tr': 'Profesyonel sürücü ekibimize katılın ve esnek çalışma saatleri, rekabetçi ücret ve destekleyici bir çalışma ortamının keyfini çıkarın.',
    },
    {
        'identifier': 'apply_now_button',
        'content_de': 'Bewerbung Fortsetzen',
        'content_en': 'Apply Now',
        'content_pl': 'Aplikuj teraz',
        'content_ro': 'Aplică acum',
        'content_uk': 'Подати заявку',
        'content_ar': 'تقدم الآن',
        'content_tr': 'Şimdi Başvur',
    },
    {
        'identifier': 'learn_more_button',
        'content_de': 'Mehr Erfahren',
        'content_en': 'Learn More',
        'content_pl': 'Dowiedz się więcej',
        'content_ro': 'Află mai multe',
        'content_uk': 'Дізнатися більше',
        'content_ar': 'معرفة المزيد',
        'content_tr': 'Daha Fazla Bilgi',
    },
    {
        'identifier': 'continue_application_button',
        'content_de': 'Bewerbung Fortsetzen',
        'content_en': 'Continue Application',
        'content_pl': 'Kontynuuj aplikację',
        'content_ro': 'Continuă aplicația',
        'content_uk': 'Продовжити заявку',
        'content_ar': 'متابعة التطبيق',
        'content_tr': 'Başvuruya Devam Et',
    },
    {
        'identifier': 'start_application_button',
        'content_de': 'Bewerbung Jetzt Starten',
        'content_en': 'Start Your Application Now',
        'content_pl': 'Rozpocznij aplikację teraz',
        'content_ro': 'Începeți aplicația acum',
        'content_uk': 'Почніть заявку зараз',
        'content_ar': 'ابدأ طلبك الآن',
        'content_tr': 'Başvurunuzu Şimdi Başlatın',
    },
    {
        'identifier': 'cta_title',
        'content_de': 'Bereit, unserem Team beizutreten?',
        'content_en': 'Ready to Join Our Team?',
        'content_pl': 'Gotowy dołączyć do naszego zespołu?',
        'content_ro': 'Gata să vă alăturați echipei noastre?',
        'content_uk': 'Готові приєднатися до нашої команди?',
        'content_ar': 'هل أنت مستعد للانضمام إلى فريقنا؟',
        'content_tr': 'Ekibimize Katılmaya Hazır mısınız?',
    },
    {
        'identifier': 'cta_subtitle',
        'content_de': 'Starten Sie Ihre Reise als Lieferfahrer noch heute und genießen Sie Freiheit, Flexibilität und wettbewerbsfähige Verdienstmöglichkeiten.',
        'content_en': 'Start your journey as a delivery driver today and enjoy the freedom, flexibility, and competitive earnings.',
        'content_pl': 'Rozpocznij swoją podróż jako kierowca dostawczy już dziś i ciesz się wolnością, elastycznością i konkurencyjnymi zarobkami.',
        'content_ro': 'Începeți-vă călătoria ca șofer de livrare astăzi și bucurați-vă de libertate, flexibilitate și câștiguri competitive.',
        'content_uk': 'Почніть свою подорож як водій доставки сьогодні та насолоджуйтесь свободою, гнучкістю та конкурентним заробітком.',
        'content_ar': 'ابدأ رحلتك كسائق توصيل اليوم واستمتع بالحرية والمرونة والأرباح التنافسية.',
        'content_tr': 'Kurye olarak yolculuğunuza bugün başlayın ve özgürlüğün, esnekliğin ve rekabetçi kazançların tadını çıkarın.',
    },
    {
        'identifier': 'cta_button',
        'content_de': 'Jetzt Bewerben',
        'content_en': 'Apply Now',
        'content_pl': 'Aplikuj teraz',
        'content_ro': 'Aplică acum',
        'content_uk': 'Подати заявку',
        'content_ar': 'تقدم الآن',
        'content_tr': 'Şimdi Başvur',
    },
]

# Create content items
for item in content_items:
    # Check if the item already exists
    existing_item = EditableContent.objects.filter(identifier=item['identifier']).first()
    if existing_item:
        print(f"Content '{item['identifier']}' already exists, updating...")
        for key, value in item.items():
            if key != 'identifier':  # Don't update the identifier
                setattr(existing_item, key, value)
        existing_item.save()
    else:
        print(f"Creating new content '{item['identifier']}'...")
        EditableContent.objects.create(**item)

print("Content seeding complete!")