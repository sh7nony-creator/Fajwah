import json
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
from src.data import load_regional_bundle, METRICS, ORGS
from src.presentation import prepare_regional, fields, row_details, interpretation, DENSITY, COUNT
from src.regional_views import map_figure, ranking_figure, comparison_figure, results_table, gap_color, RED, TEAL

ROOT = Path(__file__).resolve().parents[1]

class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original, cls.geo = load_regional_bundle()
        cls.frame = prepare_regional(cls.original)

    def test_derivatives_preserve_excel_columns_and_precision(self):
        pd.testing.assert_frame_equal(self.frame[self.original.columns], self.original)
        for metric in METRICS:
            m = fields(metric)
            national = self.original[ORGS].sum() / self.original[m['base']].sum() * m['scale']
            regional = self.original[ORGS] / self.original[m['base']] * m['scale']
            np.testing.assert_allclose(self.frame[m['national']], national, rtol=1e-12)
            np.testing.assert_allclose(self.frame[m['density']], regional, rtol=1e-12)
            np.testing.assert_allclose(self.frame[m['density_gap']], national-regional, rtol=1e-12)
            np.testing.assert_allclose(self.frame[m['density_gap']], -self.original[m['gap']] / self.original[m['base']] * m['scale'], atol=1e-12)
            np.testing.assert_allclose(self.original[m['expected']].sum(), self.original[ORGS].sum(), atol=1e-8)
            np.testing.assert_allclose(self.original[m['gap']].sum(), 0, atol=1e-8)

    def test_relative_and_count_ranks_independent(self):
        for metric in METRICS:
            m = fields(metric)
            expected = self.frame[m['density_gap']].rank(method='min', ascending=False)
            np.testing.assert_equal(self.frame[m['density_rank']].to_numpy(), expected.to_numpy())
            np.testing.assert_equal(self.frame[m['rank']].to_numpy(), self.original[m['rank']].to_numpy())
        # Density ranking is meaningfully different from the numeric difference ranking.
        self.assertFalse((self.frame['population_density_rank'] == self.frame['Population Gap Rank']).all())

    def test_missing_values_fail_instead_of_zero_fill(self):
        for column in ['Population', ORGS, 'Total Elderly Population (60+)', 'Population Gap', 'Elderly Gap']:
            broken = self.original.copy()
            broken.loc[0, column] = np.nan
            with self.assertRaises(ValueError):
                prepare_regional(broken)

    def test_all_visuals_match_card_values_for_both_bases(self):
        for metric in METRICS:
            for basis in [DENSITY, COUNT]:
                m = fields(metric, basis)
                fig = map_figure(self.frame, self.geo, metric, 'الشرقية', basis)
                rank = ranking_figure(self.frame, metric, 'الشرقية', basis)
                compare = comparison_figure(self.frame, metric, 'الشرقية', basis)
                table = results_table(self.frame, metric, basis)
                for i, region in enumerate(self.frame.Region):
                    details = row_details(self.frame, metric, region, basis)
                    j = list(rank.data[0].y).index(region)
                    row = table.loc[table['المنطقة'] == region].iloc[0]
                    self.assertAlmostEqual(fig.data[0].z[i], details['value'], places=12)
                    self.assertAlmostEqual(rank.data[0].x[j], details['value'], places=12)
                    self.assertAlmostEqual(compare.data[0].x[j], details['actual'], places=12)
                    self.assertAlmostEqual(compare.data[1].x[j], details['expected'], places=12)
                    self.assertAlmostEqual(row['فرق الجهات (جهة)'], details['count_gap'], places=12)
                    self.assertAlmostEqual(row['فجوة الكثافة · '+m['unit']], details['density_gap'], places=12)
                values = list(rank.data[0].x)
                self.assertEqual(values, sorted(values, reverse=basis == DENSITY))

    def test_colors_stable_and_zero_centered(self):
        for metric in METRICS:
            for basis in [DENSITY, COUNT]:
                a = map_figure(self.frame, self.geo, metric, 'الشرقية', basis)
                b = map_figure(self.frame, self.geo, metric, 'الرياض', basis)
                self.assertEqual(a.data[0].zmin, b.data[0].zmin)
                self.assertEqual(a.data[0].zmax, -a.data[0].zmin)
                for region, expected in [('الشرقية', RED), ('الرياض', TEAL)]:
                    detail = row_details(self.frame, metric, region, basis)
                    self.assertEqual(gap_color(detail['value'], basis), expected)

    def test_rule_based_interpretation(self):
        for metric in METRICS:
            for region, direction in [('الشرقية', 'أقل'), ('الرياض', 'أعلى')]:
                text = interpretation(row_details(self.frame, metric, region), metric)
                self.assertIn(direction, text)
                self.assertIn('%', text)
                if metric == 'elderly':
                    self.assertIn('ولا يمثل قياسًا مباشرًا', text)

    def test_switches_do_not_mix_metric_payloads(self):
        app = AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
        for region in ['الشرقية', 'الرياض']:
            app.selectbox(key='region').select(region).run(timeout=30)
            for metric in METRICS:
                app.radio(key='metric').set_value(metric).run(timeout=30)
                for basis in [DENSITY, COUNT]:
                    app.selectbox(key='basis').select(basis).run(timeout=30)
                    self.assertEqual(len(app.exception), 0)
                    self.assertEqual(len(app.error), 0)
                    self.assertEqual(app.selectbox(key='region').value, region)
                    m = fields(metric, basis)
                    specs = [json.loads(element.proto.spec) for element in app.get('plotly_chart')]
                    main = next(spec['data'][0] for spec in specs if spec['data'][0]['type'] == 'choroplethmap')
                    np.testing.assert_allclose(main['z'], self.frame[m['value']])
                    table = app.dataframe[0].value
                    self.assertIn('فجوة الكثافة · '+m['unit'], table.columns)
                    other = fields('elderly' if metric == 'population' else 'population')
                    self.assertNotIn('فجوة الكثافة · '+other['unit'], table.columns)
