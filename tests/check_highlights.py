"""Exercise the actual player's highlighter in Chromium without external CDNs."""

import re
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    html = (Path(__file__).resolve().parents[1] / 'index.html').read_text()
    function = html[html.index('function drawHighlight(sentence) {'):html.index('function showStatus(')]
    css = re.search(r'\.highlight-box\s*\{[^}]+\}', html).group(0)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=shutil.which('chromium'),
                                    args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1000, 'height': 800})
        page.set_content('<style>#highlight-overlay-1{position:relative;width:400px;height:600px}'
                         + css + '</style><canvas id="pdf-canvas-1"></canvas><div id="highlight-overlay-1"></div>')
        page.add_script_tag(content='let currentHighlight=null;let highlightOffset=0;'
                            'let pageViewports={1:{width:600,height:900}};' + function)
        # Pixel coordinates from a 2x render; stay inside the right column.
        page.evaluate('''drawHighlight({location:{page_number:1,coordinate_width:1200,coordinate_height:1800,
            points:[[660,180],[1140,180],[1140,360],[660,360]]}})''')
        box = page.locator('.highlight-box').bounding_box()
        overlay = page.locator('#highlight-overlay-1').bounding_box()
        assert abs(box['x'] - overlay['x'] - 220) < 1, box
        assert abs(box['width'] - 160) < 1, box
        assert abs(box['height'] - 60) < 1, box
        # Responsive scaling should not depend on the canvas's bitmap dimensions.
        page.locator('#highlight-overlay-1').evaluate('(el)=>{el.style.width="200px";el.style.height="300px"}')
        page.wait_for_timeout(250)
        assert abs(page.locator('.highlight-box').bounding_box()['width'] - 80) < 1
        # Old PDF-point manifests keep working without coordinate dimensions.
        page.evaluate('''drawHighlight({location:{page_number:1,
            points:[[0,0],[300,0],[300,90],[0,90]]}})''')
        assert page.locator('.highlight-box').count() == 1
        assert page.locator('.highlight-box').evaluate('(el)=>el.style.width') == '50%'
        # Invalid output removes the previous highlight and does not create one.
        page.evaluate('drawHighlight({location:{page_number:1,points:[[0,0],[0,0],[0,0]]}})')
        assert page.locator('.highlight-box').count() == 0
        browser.close()
    print('Highlight checks passed: columns, image coordinates, responsive scaling, legacy manifests, invalid boxes.')


if __name__ == '__main__':
    main()
