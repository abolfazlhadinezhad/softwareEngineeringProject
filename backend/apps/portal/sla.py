from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from rest_framework.exceptions import ValidationError


def _windows(start, calendar):
    zone = ZoneInfo(calendar.timezone)
    local = start.astimezone(zone)
    holidays = set(calendar.holidays.values_list('date', flat=True))
    if not calendar.weekdays or calendar.opens >= calendar.closes:
        raise ValidationError('تقویم کاری معتبر نیست.')
    day = local.date()
    for _ in range(366 * 10):
        if day.weekday() in calendar.weekdays and day not in holidays:
            yield datetime.combine(day, calendar.opens, zone), datetime.combine(day, calendar.closes, zone)
        day += timedelta(days=1)


def add_business_minutes(start, minutes, calendar):
    remaining = timedelta(minutes=minutes)
    for opens, closes in _windows(start, calendar):
        cursor = max(start, opens)
        if cursor >= closes:
            continue
        available = closes - cursor
        if remaining <= available:
            return cursor + remaining
        remaining -= available
    raise ValidationError('مدت SLA خارج از محدوده تقویم است.')


def business_minutes_between(start, end, calendar):
    total = 0
    for opens, closes in _windows(start, calendar):
        if opens >= end:
            break
        total += max(0, (min(end, closes) - max(start, opens)).total_seconds() / 60)
    return total
