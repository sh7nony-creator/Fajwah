import copy
import unittest
import pandas as pd
from src.data import load_regional, load_boundaries, METRICS
from src.regions import REGIONS, GEO_NAMES, normalize_region
from src.validation import validate_all, validate_regions, validate_metrics, validate_geometry, validate_checksums, validate_sources

class DataTests(unittest.TestCase):
    def setUp(self):
        self.frame = load_regional()
        self.geo = load_boundaries()

    def test_originals_unchanged(self):
        validate_checksums()

    def test_region_aliases(self):
        self.assertEqual(normalize_region(' المنطقة الشرقية '), 'الشرقية')
        for name, expected in GEO_NAMES.items():
            self.assertEqual(normalize_region(name), expected)
        with self.assertRaises(ValueError):
            normalize_region('غير معروفة')

    def test_thirteen_regions_and_exact_join(self):
        validate_regions(self.frame.Region)
        self.assertEqual(set(self.frame.region_id), {f['id'] for f in self.geo['features']})

    def test_missing_duplicate_and_extra_region_rejected(self):
        names = list(REGIONS)
        for invalid in [names[:-1], names[:-1] + names[:1], names + ['إضافية']]:
            with self.assertRaises(ValueError):
                validate_regions(invalid)

    def test_geometry(self):
        validate_geometry(self.geo)

    def test_invalid_geometry_rejected(self):
        invalid = copy.deepcopy(self.geo)
        invalid['features'][0]['geometry'] = {'type': 'Polygon', 'coordinates': []}
        with self.assertRaises(ValueError):
            validate_geometry(invalid)

    def test_metrics_totals_formulas_sign_and_ranks(self):
        validate_metrics(self.frame)

    def test_wrong_total_rejected(self):
        self.frame.loc[0, 'Population'] += 1
        with self.assertRaises(ValueError):
            validate_metrics(self.frame)

    def test_sign_and_rank_errors_rejected(self):
        for metric in METRICS.values():
            for field in ['gap', 'rank', 'expected']:
                broken = self.frame.copy()
                broken.loc[0, metric[field]] += 10
                with self.assertRaises(ValueError):
                    validate_metrics(broken)
            inverted = self.frame.copy()
            inverted[metric['gap']] *= -1
            with self.assertRaises(ValueError):
                validate_metrics(inverted)

    def test_reports_and_raw_inputs(self):
        validate_sources(self.frame)

    def test_metric_identity(self):
        self.assertNotEqual(METRICS['population']['gap'], METRICS['elderly']['gap'])
        self.assertEqual(self.frame.loc[self.frame['Population Gap Rank'].idxmin(), 'Region'], 'الشرقية')
        self.assertEqual(self.frame.loc[self.frame['Elderly Gap Rank'].idxmin(), 'Region'], 'مكة المكرمة')

    def test_full_pipeline_and_no_mutation(self):
        original = self.frame.copy(deep=True)
        self.assertEqual(validate_all(self.frame, self.geo)['status'], 'passed')
        pd.testing.assert_frame_equal(original, self.frame)

if __name__ == '__main__':
    unittest.main()
