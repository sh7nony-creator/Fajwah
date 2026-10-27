import unittest
import json
from urllib.parse import unquote
from pathlib import Path
from streamlit.testing.v1 import AppTest
from src.data import load_regional_bundle, POP, ELDERLY
from src.presentation import prepare_regional, row_details, fields
from src.regional_ui import status, insight_head, mini_cards, count_comparison
from src.regional_views import gap_color, map_figure, ranking_figure

ROOT = Path(__file__).resolve().parents[1]

class RegionalDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        approved, cls.geo = load_regional_bundle()
        cls.frame = prepare_regional(approved)

    def test_insight_markup_displays_approved_numbers(self):
        for metric in ['population','elderly']:
            for region in ['الشرقية','الرياض']:
                for basis in ['density','count']:
                    details = row_details(self.frame,metric,region,basis)
                    row = self.frame.loc[self.frame.Region == region].iloc[0]
                    head = insight_head(details,fields(metric,basis),basis,gap_color(details['value'],basis))
                    self.assertIn(f'{details["value"]:+,.2f}',head)
                    self.assertIn(region,head)
                    mini = mini_cards(row,details,POP,ELDERLY)
                    for number in [f'{int(row[POP]):,}',f'{int(row[ELDERLY]):,}',f'{details["actual"]:,}']:
                        self.assertIn(number,mini)
                    comparison = count_comparison(details,status(details)[1])
                    self.assertIn(f'{details["expected"]:,.2f}',comparison)
                    self.assertIn(f'{details["count_gap"]:+,.2f}',comparison)

    def test_status_direction_preserved_across_bases(self):
        for metric in ['population','elderly']:
            for region,label in [('الشرقية','أقل من المرجع'),('الرياض','أعلى من المرجع')]:
                for basis in ['density','count']:
                    self.assertEqual(status(row_details(self.frame,metric,region,basis))[0],label)

    def test_snow_map_keeps_every_boundary_and_selected_outline(self):
        fig = map_figure(self.frame,self.geo,'population','الشرقية')
        self.assertEqual(len(fig.data[0].locations),13)
        map_style = json.loads(unquote(fig.layout.map.style.split(',',1)[1]))
        self.assertEqual(map_style['sources'],{})
        self.assertEqual(fig.data[1].locations[0],'SA-04')
        self.assertEqual(map_style['layers'][0]['paint']['background-color'],'#F7F9FB')
        self.assertEqual(fig.data[1].marker.line.color,'#292D38')
        self.assertEqual(len(fig.data[0].z),13)

    def test_navigation_and_widget_contracts(self):
        app = AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
        self.assertEqual(len(app.exception),0)
        self.assertEqual(len(app.error),0)
        self.assertEqual(len(app.get('page_link')),3)
        self.assertEqual(app.radio(key='metric').value,'population')
        self.assertEqual(app.selectbox(key='basis').value,'density')
        self.assertEqual(len(app.selectbox(key='region').options),13)
        self.assertEqual(len(app.get('plotly_chart')),7)
