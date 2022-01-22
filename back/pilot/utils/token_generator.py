import random

# Using non-deprecated elements of the string module.
# pylint: disable=W0402
import string
# pylint: enable=W0402


def generate_token(size=32):
    """Generates a random token containing only ascii letters and digits."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in range(size))
