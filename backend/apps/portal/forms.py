from datetime import date, time

from rest_framework.exceptions import ValidationError

TYPES = {'text', 'textarea', 'number', 'select', 'multiselect', 'checkbox', 'radio', 'date', 'time'}


def validate_fields(fields):
    if not isinstance(fields, list) or len(fields) > 60:
        raise ValidationError({'fields': 'فرم باید حداکثر ۶۰ فیلد داشته باشد.'})
    keys = set()
    for field in fields:
        if not isinstance(field, dict) or field.get('type') not in TYPES or not isinstance(field.get('key'), str) or not field['key'].isidentifier():
            raise ValidationError({'fields': 'نوع یا شناسه فیلد معتبر نیست.'})
        if field['key'] in keys or not field.get('label') or any(word in field['key'].lower() for word in ('password', 'secret', 'token')):
            raise ValidationError({'fields': 'شناسه تکراری یا دریافت رمز و اطلاعات محرمانه مجاز نیست.'})
        keys.add(field['key'])
        if field['type'] in ('select', 'multiselect', 'radio') and (not isinstance(field.get('options'), list) or not field['options'] or not all(isinstance(x, str) for x in field['options'])):
            raise ValidationError({'fields': 'گزینه‌های فیلد را مشخص کنید.'})
        if field.get('visible_when') and field['visible_when'].get('field') not in keys - {field['key']}:
            raise ValidationError({'fields': 'شرط نمایش باید به فیلد قبلی اشاره کند.'})
    return fields


def validate_submission(form, responses):
    if not isinstance(responses, dict):
        raise ValidationError({'form_responses': 'پاسخ فرم معتبر نیست.'})
    if form is None:
        if responses:
            raise ValidationError({'form_responses': 'فرم اضافه‌ای برای این دسته تعریف نشده است.'})
        return {}, {}
    if not form.is_active:
        raise ValidationError({'category': 'فرم این دسته غیرفعال است.'})
    fields = validate_fields(form.fields)
    cleaned, errors = {}, {}
    if set(responses) - {f['key'] for f in fields}:
        raise ValidationError({'form_responses': 'فیلد ناشناخته در فرم وجود دارد.'})
    for field in fields:
        key, kind = field['key'], field['type']
        condition = field.get('visible_when')
        if condition and responses.get(condition['field']) != condition.get('equals'):
            continue
        value = responses.get(key)
        if value is None or value == '' or value == []:
            if field.get('required'):
                errors[key] = 'این فیلد الزامی است.'
            continue
        valid = True
        if kind in ('text', 'textarea'):
            valid = isinstance(value, str) and len(value) <= min(int(field.get('max_length', 5000)), 10000)
        elif kind == 'number':
            valid = isinstance(value, (int, float)) and not isinstance(value, bool) and field.get('min', -1e15) <= value <= field.get('max', 1e15)
        elif kind in ('select', 'radio'):
            valid = value in field['options']
        elif kind == 'multiselect':
            valid = isinstance(value, list) and all(x in field['options'] for x in value)
        elif kind == 'checkbox':
            valid = isinstance(value, bool)
        elif kind in ('date', 'time'):
            try:
                (date if kind == 'date' else time).fromisoformat(value)
            except (TypeError, ValueError):
                valid = False
        if valid:
            cleaned[key] = value
        else:
            errors[key] = 'مقدار واردشده معتبر نیست.'
    if errors:
        raise ValidationError({'form_responses': errors})
    return {'id': form.pk, 'name': form.name, 'version': form.version, 'fields': fields}, cleaned
