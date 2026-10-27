"""Independent checks of approved files; failures never repair inputs."""
import hashlib
import json
import numpy as np
import pandas as pd
from shapely.geometry import shape
from .data import RAW, REFERENCE, POP, ORGS, ELDERLY, METRICS, read_table
from .regions import REGIONS, normalize_region

TOTALS = {POP: 32175224, ORGS: 2645, ELDERLY: 1758737}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def close(actual, expected, message):
    require(np.allclose(actual, expected, rtol=1e-10, atol=1e-8), message)

def validate_regions(names):
    names = list(names)
    require(len(names) == 13 and len(set(names)) == 13 and set(names) == set(REGIONS),
            'يجب وجود المناطق الثلاث عشرة مرة واحدة دون مناطق مفقودة أو إضافية')

def validate_geometry(geo):
    require(geo.get('type') == 'FeatureCollection', 'صيغة الحدود غير صحيحة')
    features = geo['features']
    validate_regions(f['properties']['region_name_ar'] for f in features)
    require(len({f['id'] for f in features}) == 13, 'معرفات حدود مكررة')
    for f in features:
        props = f['properties']
        require(f['id'] == props['region_id'] == props['shapeISO'] == REGIONS[props['region_name_ar']], 'تعارض معرف الحدود')
        require(props['shapeGroup'] == 'SAU' and props['shapeType'] == 'ADM1', 'مستوى حدود غير مناسب')
        geom = shape(f['geometry'])
        require(geom.geom_type in ('Polygon', 'MultiPolygon') and not geom.is_empty and geom.is_valid,
                f"هندسة حدود غير صالحة: {f['id']}")
        x1, y1, x2, y2 = geom.bounds
        require(33 < x1 < x2 < 57 and 15 < y1 < y2 < 34, 'نطاق إحداثيات غير متوقع')

def validate_metrics(frame):
    validate_regions(frame['Region'])
    require(frame['region_id'].tolist() == frame['Region'].map(REGIONS).tolist(), 'ربط رموز غير صحيح')
    columns = [POP, ORGS, ELDERLY] + [m[k] for m in METRICS.values() for k in ('gap', 'expected', 'rank')]
    require(np.isfinite(frame[columns].to_numpy(dtype=float)).all(), 'قيم ناقصة أو غير منتهية')
    require((frame[[POP, ELDERLY]] > 0).all().all() and (frame[ORGS] >= 0).all(), 'أعداد غير صالحة')
    for column, total in TOTALS.items():
        close(frame[column].sum(), total, f'اختلاف إجمالي {column}')
    for metric in METRICS.values():
        expected = frame[ORGS].sum() * frame[metric['base']] / frame[metric['base']].sum()
        close(frame[metric['expected']], expected, 'اختلاف التوزيع المتوقع')
        close(frame[metric['expected']].sum(), frame[ORGS].sum(), 'مجموع المرجع لا يساوي إجمالي الجهات')
        close(frame[metric['gap']], frame[ORGS] - expected, 'اختلاف معادلة الفجوة أو اتجاه إشارتها')
        close(frame[metric['rank']], frame[metric['gap']].rank(method='min', ascending=True), 'اختلاف الرتب')
        close(frame[metric['gap']].sum(), 0, 'مجموع الفجوة لا يساوي صفرًا')
    close(frame['Organizations per 100,000 population'], frame[ORGS] / frame[POP] * 100000, 'معدل السكان')
    close(frame['Organizations per 10,000 elderly residents'], frame[ORGS] / frame[ELDERLY] * 10000, 'معدل كبار السن')
    close(frame['Elderly percentage of population'], frame[ELDERLY] / frame[POP] * 100, 'نسبة كبار السن')

def validate_sources(frame):
    indexed = frame.set_index('Region')
    pop = read_table('population_2024.csv.xlsx')
    elderly = read_table('elderly_by_region_2025.xlsx.xlsx')
    for raw, col, target in [(pop, 'عدد السكان', POP), (elderly, 'إجمالي كبار السن (60+)', ELDERLY)]:
        raw['المنطقة الإدارية'] = raw['المنطقة الإدارية'].map(normalize_region)
        validate_regions(raw['المنطقة الإدارية'])
        close(raw.set_index('المنطقة الإدارية')[col].reindex(indexed.index), indexed[target], 'اختلاف المدخلات الإقليمية')
    org = read_table('ncnp_orgs.csv.xlsx', header=None)
    org = org[org[3].notna() & ~org[3].isin(['المنطقة', 'المنطقة الإدارية'])].copy()
    org[3] = org[3].map(normalize_region)
    close(org.groupby(3).size().reindex(indexed.index), indexed[ORGS], 'اختلاف أعداد الجهات')
    for metric, sheet in [('population', 'Population Gap Ranking'), ('elderly', 'Elderly Gap Ranking')]:
        report = read_table('Regional_Gap_Report.xlsx', sheet)
        report['Region'] = report['Region'].map(normalize_region)
        validate_regions(report['Region'])
        pd.testing.assert_frame_equal(report.set_index('Region').reindex(indexed.index), indexed.drop(columns='region_id'), check_dtype=False, atol=1e-8)
        require(report[METRICS[metric]['gap']].is_monotonic_increasing, 'ترتيب التقرير غير تصاعدي')
    summary = read_table('Summary_Report.xlsx', 'Summary').set_index('Topic')['Finding']
    for topic, column in [('Total nonprofit organizations', ORGS), ('Population covered', POP), ('Total elderly population (60+)', ELDERLY)]:
        require(int(str(summary[topic]).replace(',', '')) == TOTALS[column], 'اختلاف إجمالي الملخص')
    priority = read_table('Summary_Report.xlsx', 'Priority Regions')
    expected = frame[(frame['Population Gap'] < 0) & (frame['Elderly Gap'] < 0)].sort_values(['Population Gap Rank', 'Elderly Gap Rank'])
    pd.testing.assert_frame_equal(priority.reset_index(drop=True), expected.drop(columns='region_id').reset_index(drop=True), check_dtype=False, atol=1e-8)

def validate_checksums():
    for name, digest in json.loads((REFERENCE / 'raw_checksums.json').read_text()).items():
        require(hashlib.sha256((RAW / name).read_bytes()).hexdigest() == digest, f'تغير ملف أصلي: {name}')
    digest = (REFERENCE / 'boundary_sha256.txt').read_text().split()[0]
    require(hashlib.sha256((REFERENCE / 'saudi_adm1.geojson').read_bytes()).hexdigest() == digest,
            'تغير ملف الحدود الأصلي')

def validate_all(frame, geo):
    validate_checksums()
    validate_metrics(frame)
    validate_geometry(geo)
    require(set(frame['region_id']) == {f['id'] for f in geo['features']}, 'عدم تطابق Excel والحدود')
    validate_sources(frame)
    return {'regions': 13, 'totals': TOTALS.copy(), 'status': 'passed'}
