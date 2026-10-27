"""Read approved results. Never write or recalculate source files."""
from pathlib import Path
import json
import pandas as pd
from .regions import REGIONS, normalize_region

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
REFERENCE = ROOT / 'data' / 'reference'
POP = 'Population'
ORGS = 'Number of Nonprofit Organizations'
ELDERLY = 'Total Elderly Population (60+)'
METRICS = {
    'population': {'label': 'الفجوة السكانية', 'gap': 'Population Gap',
                   'expected': 'Expected_Organizations_Population', 'rank': 'Population Gap Rank', 'base': POP},
    'elderly': {'label': 'فجوة التوزيع وفق كبار السن', 'gap': 'Elderly Gap',
                'expected': 'Expected_Organizations_Elderly', 'rank': 'Elderly Gap Rank', 'base': ELDERLY},
}

def read_table(filename, sheet_name=0, **kwargs):
    return pd.read_excel(RAW / filename, sheet_name=sheet_name, engine='openpyxl', **kwargs)

def with_regions(frame, column='Region'):
    frame = frame.copy(deep=True)
    frame[column] = frame[column].map(normalize_region)
    frame['region_id'] = frame[column].map(REGIONS)
    return frame

def load_regional():
    return with_regions(read_table('Master_Dataset.xlsx', 'Master Dataset'))

def load_boundaries():
    # json.load creates a new object; original geometries and properties remain on disk.
    geo = json.loads((REFERENCE / 'saudi_adm1.geojson').read_text(encoding='utf-8'))
    for feature in geo['features']:
        props = feature['properties']
        name = normalize_region(props['shapeName'])
        if props['shapeISO'] != REGIONS[name]:
            raise ValueError(f'تعارض الاسم ورمز المنطقة: {name}')
        props.update(region_name_ar=name, region_id=REGIONS[name])
        feature['id'] = REGIONS[name]
    return geo

def load_regional_bundle():
    from .validation import validate_all
    frame, boundaries = load_regional(), load_boundaries()
    validate_all(frame, boundaries)
    return frame, boundaries
