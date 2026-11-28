import re
import unicodedata


def normalize(value):
    value = unicodedata.normalize('NFKC', str(value)).translate(str.maketrans('يك٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', 'یک01234567890123456789'))
    return re.sub(r'\s+', ' ', value.replace('\u200c', ' ').replace('\u200f', '').replace('\u0640', '')).strip().lower()
