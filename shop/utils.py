from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_order_email(name, phone_number, location, products, email_template="emails/order-for-email.html"):
    context = {
        "products": products,
        "name": name,
        "phone_number": phone_number,
        "location": location,
    }
    html_content = render_to_string(email_template, context)
    email = EmailMessage(
        "Новый заказ!",
        html_content,
        "aquamarine.solotvino@gmail.com",
        ["aquamarine.solotvino@gmail.com"],
    )
    email.content_subtype = "html"
    email.send()


def ukrainian_to_latin(text):
    transliteration_table = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D',
        'Е': 'E', 'Є': 'Ye', 'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I',
        'Ї': 'Yi', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sh',
        'Ю': 'Yu', 'Я': 'Ya', 'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h',
        'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ie', 'ж': 'zh', 'з': 'z',
        'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i', 'к': 'k', 'л': 'l',
        'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's',
        'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'sh', 'ь': '', 'ю': 'iu', 'я': 'ia', '’': '',
        'ъ': '', 'ы': 'y', 'э': 'e', 'ё': 'e'
    }
    return ''.join(transliteration_table.get(c, c) for c in text)
