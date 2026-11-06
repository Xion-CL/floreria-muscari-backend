import re

from django.core.exceptions import ValidationError


def normalizar_rut(valor):
    """'12.345.678-5' -> '12345678-5' (DV en mayúscula)."""
    limpio = re.sub(r'[.\s-]', '', valor or '').upper()
    if len(limpio) < 2:
        return limpio
    return f'{limpio[:-1]}-{limpio[-1]}'


def validar_rut(valor):
    """Valida un RUT chileno con el algoritmo del dígito verificador (módulo 11)."""
    rut = normalizar_rut(valor)
    if not re.fullmatch(r'\d{7,8}-[\dK]', rut):
        raise ValidationError('Ingresa un RUT válido, por ejemplo 12.345.678-5.')
    cuerpo, dv = rut.split('-')
    suma, factor = 0, 2
    for digito in reversed(cuerpo):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    esperado = '0' if resto == 11 else 'K' if resto == 10 else str(resto)
    if dv != esperado:
        raise ValidationError('El RUT ingresado no es válido (dígito verificador incorrecto).')
    return rut
