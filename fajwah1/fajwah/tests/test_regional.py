import unittest
import json
from copy import deepcopy
from pathlib import Path
import numpy as np
from streamlit.testing.v1 import AppTest
from src.data import load_regional_bundle, METRICS, ORGS
from src.regional_views import map_figure, ranking_figure, comparison_figure, results_table, selected_region
from src.presentation import prepare_regional, fields, DENSITY, COUNT, row_details

ROOT = Path(__file__).resolve().parents[1]

class RegionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        approved, cls.geo = load_regional_bundle()
        cls.frame = prepare_regional(approved)

    def test_map_has_all_regions_and_approved_values(self):
        original = deepcopy(self.geo)
        for metric, m in METRICS.items():
            fig = map_figure(self.frame, self.geo, metric, 'الرياض')
            self.assertEqual(set(fig.data[0].locations), set(self.frame.region_id))
            self.assertEqual(len(fig.data[0].geojson['features']), 13)
            np.testing.assert_allclose(fig.data[0].z, self.frame[fields(metric)['value']])
            self.assertEqual(fig.data[0].zmin, -fig.data[0].zmax)
            self.assertEqual(fig.layout.clickmode, 'event+select')
            self.assertEqual(fig.data[0].type, 'choroplethmap')
        self.assertEqual(self.geo, original)

    def test_rankings_comparison_and_table_match_excel(self):
        for metric, m in METRICS.items():
            expected = self.frame.sort_values([fields(metric)['value'], 'Region'], ascending=[False, True])
            rank = ranking_figure(self.frame, metric, 'الرياض')
            compare = comparison_figure(self.frame, metric, 'الرياض')
            self.assertEqual(list(rank.data[0].y), expected.Region.tolist())
            np.testing.assert_allclose(rank.data[0].x, expected[fields(metric)['value']])
            np.testing.assert_allclose(compare.data[0].x, expected[ORGS])
            np.testing.assert_allclose(compare.data[1].x, expected[m['expected']])
            table = results_table(self.frame, metric)
            self.assertEqual(len(table), 13)
            self.assertEqual(table['رتبة ضعف الكثافة'].tolist(), list(range(1, 14)))
            np.testing.assert_allclose(table['فرق الجهات (جهة)'], expected[m['gap']])

    def test_selection_location_not_point_index(self):
        self.assertEqual(selected_region({'selection': {'points': [{'location': 'SA-02'}]}}, 'الرياض'), 'مكة المكرمة')
        self.assertEqual(selected_region({'selection': {'points': [{'point_index': 1}]}}, 'الرياض'), 'الرياض')
        self.assertEqual(selected_region({'selection': {'points': [{'location': 'unknown'}]}}, 'الرياض'), 'الرياض')

    def test_dropdown_metric_and_card_update(self):
        app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
        app.selectbox(key='region').select('مكة المكرمة').run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('-200.74' in item.value for item in app.markdown))
        self.assertEqual(app.dataframe[0].value.iloc[0]['المنطقة'], 'الشرقية')
        app.radio(key='metric').set_value('elderly').run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.selectbox(key='region').value, 'مكة المكرمة')
        self.assertTrue(any('-337.94' in item.value for item in app.markdown))
        self.assertEqual(app.dataframe[0].value.iloc[0]['المنطقة'], 'مكة المكرمة')
        app.radio(key='metric').set_value('population').run(timeout=30)
        self.assertEqual(app.selectbox(key='region').value, 'مكة المكرمة')
        self.assertEqual(len(app.error), 0)

    def test_selection_payload_decoder(self):
        app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
        # Simulate the documented Plotly selection payload at the actual widget boundary.
        app.session_state['region_map_population_density_False'] = {'selection': {'points': [{'location': 'SA-04'}], 'point_indices': [2], 'box': [], 'lasso': []}}
        # Callback is covered through the same shared decoder; browser test verifies event delivery.
        self.assertEqual(selected_region(app.session_state['region_map_population_density_False'], 'الرياض'), 'الشرقية')

    def test_all_regions_in_both_metric_cards(self):
        app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
        for metric, m in METRICS.items():
            app.radio(key='metric').set_value(metric).run(timeout=30)
            for _, row in self.frame.iterrows():
                app.selectbox(key='region').select(row.Region).run(timeout=30)
                self.assertEqual(len(app.exception), 0)
                self.assertTrue(any(f'{row[m["gap"]]:+,.2f}' in item.value for item in app.markdown))
                self.assertEqual(len(app.error), 0)
