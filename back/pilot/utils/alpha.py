import re
import unicodedata

from django.utils.encoding import force_text


def to_alpha(value, to_lower=True):
    """
    Normalize any unicode string so it contains only ASCII characters.

    Optionnally, lower all characters
    """
    value = force_text(value)
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ASCII', 'ignore').decode('ascii')
    if to_lower:
        value = value.lower()
    return re.sub(r'[^\w\s_-]', '', value)
