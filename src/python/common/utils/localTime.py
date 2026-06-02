from datetime import datetime
from zoneinfo import ZoneInfo

#Date et Heure fuseau Paris
def dateTimeParis():
    now = datetime.now(tz=ZoneInfo("Europe/Paris"))
    return now.strftime("%d/%m/%Y %H:%M")


def localtime():
    """Single source of truth for display date/time in the app."""
    return dateTimeParis()