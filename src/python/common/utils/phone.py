COUNTRY_DIAL_CODES = {
    'FRA': '+33',
    'BEL': '+32',
    'CHE': '+41',
    'DEU': '+49',
    'ESP': '+34',
    'ITA': '+39',
    'GBR': '+44',
    'USA': '+1',
    'CAN': '+1',
}


def get_country_dial_code(country):
    if not country:
        return ''

    stored_dial = getattr(country, 'phone_dial_code', '') or ''
    stored_dial = stored_dial.strip()
    if stored_dial:
        digits = ''.join(ch for ch in stored_dial if ch.isdigit())
        return f'+{digits}' if digits else ''

    country_iso3 = (getattr(country, 'iso3', None) or '').strip().upper()
    return COUNTRY_DIAL_CODES.get(country_iso3, '')


def normalize_phone_number(raw_phone, country_iso3=None, dial_code=None):
    if raw_phone is None:
        return ''

    cleaned = ''.join(ch for ch in str(raw_phone).strip() if ch.isdigit() or ch == '+')
    if not cleaned:
        return ''

    if cleaned.startswith('+'):
        digits = ''.join(ch for ch in cleaned[1:] if ch.isdigit())
        return f'+{digits}' if digits else ''

    digits = ''.join(ch for ch in cleaned if ch.isdigit())
    if not digits:
        return ''

    resolved_dial_code = dial_code
    if not resolved_dial_code:
        country_key = (country_iso3 or '').strip().upper()
        resolved_dial_code = COUNTRY_DIAL_CODES.get(country_key)

    if not resolved_dial_code:
        return digits

    normalized_dial = '+' + ''.join(ch for ch in str(resolved_dial_code) if ch.isdigit())
    if not normalized_dial or normalized_dial == '+':
        return digits

    return f"{normalized_dial}{digits.lstrip('0')}"
