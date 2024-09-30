import re

from django.core.exceptions import ValidationError


def hex_color_validator(value):

    if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
        raise ValidationError(
            'Введённое значение не является HEX цветом'
        )
    return value


def username_validator(value):
    restr_symb = ''.join(set(re.findall(r'[^\w.@+-]', value)))
    if restr_symb:
        raise ValidationError(
            f'Недопустимые символы в имени пользователя: {restr_symb}'
        )
    return value
