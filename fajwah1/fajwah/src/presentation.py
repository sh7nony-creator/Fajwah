"""Derived interface indicators only. Never write into approved workbooks."""
import numpy as np
from .data import METRICS, ORGS
from .validation import validate_metrics

DENSITY = 'density'
COUNT = 'count'
BASES = {DENSITY: 'ضعف الكثافة النسبي', COUNT: 'فرق الجهات العددي عن المرجع'}
ELDERLY_NOTE = 'يقيس هذا المؤشر مدى توافق توزيع إجمالي الجهات غير الربحية مع توزيع كبار السن بين المناطق، ولا يمثل قياسًا مباشرًا للخدمات المتخصصة المقدمة لهم.'

def fields(metric, basis=DENSITY):
    m = METRICS[metric]
    scale = 100000 if metric == 'population' else 10000
    unit = 'جهة لكل 100 ألف نسمة' if metric == 'population' else 'جهة لكل 10 آلاف من كبار السن (60+)'
    return dict(m, scale=scale, unit=unit, density=f'{metric}_density', national=f'{metric}_national',
        density_gap=f'{metric}_density_gap', relative=f'{metric}_relative_pct', density_rank=f'{metric}_density_rank',
        value=f'{metric}_density_gap' if basis == DENSITY else m['gap'],
        active_rank=f'{metric}_density_rank' if basis == DENSITY else m['rank'],
        value_unit=unit if basis == DENSITY else 'جهة',
        title='فجوة الكثافة' if basis == DENSITY else 'فرق الجهات العددي عن المرجع')

def prepare_regional(frame):
    validate_metrics(frame)  # Do not derive or display a result from a failed approved input.
    result = frame.copy(deep=True)
    for key in METRICS:
        m = fields(key)
        national = frame[ORGS].sum() / frame[m['base']].sum() * m['scale']
        result[m['density']] = frame[ORGS] / frame[m['base']] * m['scale']
        result[m['national']] = national
        result[m['density_gap']] = national - result[m['density']]
        result[m['relative']] = result[m['density_gap']] / national * 100
        result[m['density_rank']] = result[m['density_gap']].rank(method='min', ascending=False).astype(int)
    return result

def ensure_prepared(frame):
    return frame if 'population_density_gap' in frame else prepare_regional(frame)

def row_details(frame, metric, region, basis=DENSITY):
    m = fields(metric, basis)
    row = ensure_prepared(frame).loc[frame.Region == region].iloc[0]
    return dict(region=region, value=float(row[m['value']]), rank=int(row[m['active_rank']]),
        density=float(row[m['density']]), national=float(row[m['national']]),
        density_gap=float(row[m['density_gap']]), relative_pct=float(row[m['relative']]),
        actual=int(row[ORGS]), expected=float(row[m['expected']]),
        count_gap=float(row[m['gap']]), count_rank=int(row[m['rank']]),
        density_rank=int(row[m['density_rank']]))

def interpretation(details, metric):
    gap, pct = details['density_gap'], details['relative_pct']
    unit = fields(metric)['unit']
    if np.isclose(gap, 0, atol=1e-10, rtol=0):
        text = 'كثافة الجهات في المنطقة مطابقة للمعدل الوطني تقريبًا.'
    else:
        direction = 'أقل' if gap > 0 else 'أعلى'
        text = (f'كثافة إجمالي الجهات غير الربحية في {details["region"]} {direction} من المعدل الوطني بنسبة '
                f'{abs(pct):,.2f}%: {details["density"]:,.2f} مقابل {details["national"]:,.2f} {unit}. '
                f'فجوة الكثافة (الوطني − المنطقة) {gap:+,.2f} {unit}. ')
        if gap > 0:
            text += 'تشير المقارنة إلى ضعف نسبي في توزيع الجهات يستدعي دراسة الاحتياج بصورة أعمق. '
    return text + (' ' + ELDERLY_NOTE if metric == 'elderly' else
        ' لا تثبت هذه المقارنة نقصًا فعليًا في الخدمات؛ فهي لا تقيس نطاق الخدمة أو الطاقة التشغيلية أو انتقال المستفيدين بين المناطق.')
