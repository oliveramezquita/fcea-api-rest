import re
import tldextract


def extract_username(email):
    result = re.search(r'([\w\d\.]+)@[\w\d\.]+', email)

    if result and email.count('@') == 1:
        username = result.group(1).replace('.', '')
        return f"{username}{tldextract.extract(email).domain}"

    else:
        raise ValueError(
            f'{email} no es una dirección de correo electrónico con formato válido.')
