import io
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

import fitz

from tts_lib.chandra_extractor import ChandraExtractor, chunks_to_elements, html_to_speech
from tts_lib.pdf_extractors import get_available_extractors


class ChandraTests(unittest.TestCase):
    def test_multi_level_headers_and_spans(self):
        html = '''<table><tr><th rowspan="2">Element</th><th colspan="2">Properties</th></tr>
        <tr><th>Symbol</th><th>Number</th></tr>
        <tr><td>Oxygen</td><td>O</td><td>8</td></tr></table>'''
        self.assertEqual(html_to_speech(html),
                         'Element: Oxygen; Properties, Symbol: O; Properties, Number: 8.')

    def test_row_headers_are_data_and_rowspans_repeat(self):
        html = '''<table><tr><th>Group</th><th>Value</th></tr>
        <tr><th rowspan="2">A</th><td>1</td></tr><tr><td>2</td></tr></table>'''
        self.assertEqual(html_to_speech(html), 'Group: A; Value: 1.\n\nGroup: A; Value: 2.')

    def test_table_without_headers_keeps_blank_cells(self):
        self.assertEqual(html_to_speech('<table><tr><td>A</td><td></td></tr></table>'),
                         'Column 1: A; Column 2: blank.')

    def test_text_inline_formatting_and_paragraph_boundaries(self):
        self.assertEqual(html_to_speech('<p>A <b>bold</b> word.</p><p>Next &amp; last.</p>'),
                         'A bold word.\n\nNext & last.')

    def test_reading_order_coordinates_and_original_html(self):
        # The second block is higher on the page but belongs in the next column.
        chunks = [dict(label='Text', bbox=[0, 500, 400, 900], content='<p>Left.</p>'),
                  dict(label='Text', bbox=[600, 0, 1000, 400], content='<p>Right.</p>')]
        elements = chunks_to_elements(chunks, 7, (1000, 1000), (500, 500))
        self.assertEqual([e['text'] for e in elements], ['Left.', 'Right.'])
        self.assertEqual(elements[1]['metadata']['points'], [[300, 0], [500, 0], [500, 200], [300, 200]])
        self.assertEqual(elements[1]['metadata']['page_number'], 7)
        self.assertEqual(elements[0]['metadata']['source_html'], '<p>Left.</p>')

    def test_headers_figures_and_invalid_boxes(self):
        chunks = [dict(label=label, content=label, bbox=[0, 0, 100, 100])
                  for label in ['Page-Header', 'Page-Footer', 'Figure', 'Caption', 'Footnote']]
        chunks.append(dict(label='Text', content='Still readable', bbox=[float('nan'), 0, 50, 50]))
        elements = chunks_to_elements(chunks, 1, (100, 100), (200, 200))
        self.assertEqual([e['text'] for e in elements], ['Caption', 'Footnote', 'Still readable'])
        self.assertIsNone(elements[-1]['metadata']['points'])

    @staticmethod
    def pdf_bytes():
        with fitz.open() as pdf:
            for _ in range(3):
                pdf.new_page(width=300, height=500)
            return io.BytesIO(pdf.tobytes())

    @staticmethod
    def fake_modules(manager):
        model = types.ModuleType('chandra.model')
        model.InferenceManager = MagicMock(return_value=manager)
        schema = types.ModuleType('chandra.model.schema')
        schema.BatchInputItem = lambda **kwargs: types.SimpleNamespace(**kwargs)
        return {'chandra': types.ModuleType('chandra'), 'chandra.model': model,
                'chandra.model.schema': schema}

    def test_selected_pages_are_rendered_and_numbered(self):
        manager = MagicMock()
        manager.generate.return_value = [types.SimpleNamespace(error=False, chunks=[
            dict(label='Text', bbox=[0, 0, 300, 1000], content='<p>Hello.</p>')])]
        with patch.dict(sys.modules, self.fake_modules(manager)):
            elements = ChandraExtractor(method='vllm').extract(self.pdf_bytes(), pages=[3, 1, 3])
        self.assertEqual(manager.generate.call_count, 2)
        self.assertEqual([e['metadata']['page_number'] for e in elements], [1, 3])
        self.assertEqual(elements[0]['metadata']['points'][2], [150, 500])

    def test_page_errors_fail_before_inference(self):
        for pages in [[0], [4], [True], [1.5]]:
            with self.subTest(pages=pages), self.assertRaises(ValueError):
                ChandraExtractor().extract(self.pdf_bytes(), pages=pages)

    def test_empty_page_selection_does_not_load_model(self):
        self.assertEqual(ChandraExtractor().extract(self.pdf_bytes(), pages=[]), [])

    def test_inference_failure_does_not_become_spoken_text(self):
        manager = MagicMock()
        manager.generate.return_value = [types.SimpleNamespace(error=True)]
        with patch.dict(sys.modules, self.fake_modules(manager)), self.assertRaisesRegex(RuntimeError, 'page 2'):
            ChandraExtractor().extract(self.pdf_bytes(), pages=[2])

    def test_registration_does_not_require_model_installation(self):
        self.assertIsInstance(get_available_extractors()['chandra'], ChandraExtractor)


if __name__ == '__main__':
    unittest.main()
