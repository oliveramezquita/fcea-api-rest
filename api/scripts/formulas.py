from datetime import datetime
import hashlib


def get_es_sitio_de_referencia(value):
    """Get if it is a reference site"""
    if value == "Si":
        return True
    return False


def format_date(datetime_str, format):
    if datetime_str == '':
        return None
    return datetime.strptime(datetime_str, format)


def generate_objectid(string):
    m = hashlib.md5()
    string = string.encode('utf-8')
    m.update(string)
    unqiue_name: str = str(int(m.hexdigest(), 16))[0:12]
    return unqiue_name
