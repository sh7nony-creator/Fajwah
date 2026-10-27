import unittest
import numpy as np
from src.data import load_regional_bundle, ORGS
from src.presentation import prepare_regional, fields
from src.snow_charts import comparison_overview, density_overview, distribution_overview

class SnowChartTests(unittest.TestCase):
    def test_overview_uses_every_original_region_and_value(self):
        approved, _ = load_regional_bundle()
        frame = prepare_regional(approved)
        for metric in ['population','elderly']:
            m=fields(metric)
            line=comparison_overview(frame,metric)
            self.assertEqual(list(line.data[0].x),frame.Region.tolist())
            np.testing.assert_array_equal(line.data[0].y, frame[ORGS])
            np.testing.assert_array_equal(line.data[1].y, frame[m['expected']])
            bars=density_overview(frame,metric)
            np.testing.assert_array_equal(bars.data[0].y,frame[m['density']])
        donut=distribution_overview(frame)
        self.assertEqual(list(donut.data[0].labels),frame.Region.tolist())
        np.testing.assert_array_equal(donut.data[0].values,frame[ORGS])
