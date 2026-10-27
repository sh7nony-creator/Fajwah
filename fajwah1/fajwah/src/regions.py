import re
import unicodedata

REGIONS = {
    'الرياض': 'SA-01', 'مكة المكرمة': 'SA-02', 'المدينة المنورة': 'SA-03',
    'الشرقية': 'SA-04', 'القصيم': 'SA-05', 'حائل': 'SA-06', 'تبوك': 'SA-07',
    'الحدود الشمالية': 'SA-08', 'جازان': 'SA-09', 'نجران': 'SA-10',
    'الباحة': 'SA-11', 'الجوف': 'SA-12', 'عسير': 'SA-14',
}
GEO_NAMES = {
    'Eastern Region': 'الشرقية', 'Najran Region': 'نجران',
    'Northern Borders Region': 'الحدود الشمالية', 'Hayel Region': 'حائل',
    'Riyadh Region': 'الرياض', "'Asir Region": 'عسير', 'Makkah Region': 'مكة المكرمة',
    'Tabuk Region': 'تبوك', 'Al Madinah Region': 'المدينة المنورة',
    'Al-Qassim Region': 'القصيم', 'Al Bahah Region': 'الباحة',
    'Jazan Region': 'جازان', 'Al Jawf Region': 'الجوف',
}

def normalize_region(value):
    if not isinstance(value, str):
        raise ValueError(f'اسم منطقة غير صالح: {value!r}')
    name = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', value).replace('ـ', '')).strip()
    name = {'المنطقة الشرقية': 'الشرقية'}.get(name, GEO_NAMES.get(name, name))
    if name not in REGIONS:
        raise ValueError(f'منطقة غير معروفة: {value!r}')
    return name
