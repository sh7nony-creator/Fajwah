import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

class AppTests(unittest.TestCase):
    def test_entrypoint_and_arabic_pages(self):
        app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertEqual(app.title[0].value, 'التحليل الإقليمي')
        for page, title in [('pages/national.py', 'المؤشرات الوطنية'),
                            ('pages/methodology.py', 'المنهجية والمصادر')]:
            app.switch_page(page).run(timeout=30)
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.title[0].value, title)
