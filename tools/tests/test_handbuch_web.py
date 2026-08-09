"""Tests für handbuch-web.py gegen ein Mini-Handbuch (1 Bild, 2 Kapitel)."""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(REPO, "tools")
FIXTURE = os.path.join(TOOLS, "tests", "fixtures", "mini-handbuch")
sys.path.insert(0, TOOLS)

spec = importlib.util.spec_from_file_location("handbuch_web",
                                              os.path.join(TOOLS, "handbuch-web.py"))
handbuch_web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handbuch_web)


class TestParse(unittest.TestCase):
    def setUp(self):
        self.meta = handbuch_web.parse(FIXTURE)

    def test_title_and_claim_come_from_the_cover(self):
        # Der Deckblatt-Titel steht im Druck mit weichem Trennstrich und Zeilenumbruch:
        # "Pro&shy;be<br>&amp; Muster". Erwartet wird der Klartext — genau daran ist der
        # echte Titel "Gruppen &amp;<br>Sitzordnung" einmal zerbrochen und als
        # "Gruppen &amp;amp; Sitzordnung" auf der Seite gelandet.
        self.assertEqual(self.meta["titel"], "Probe & Muster")
        self.assertEqual(self.meta["claim"], "Nur zum Testen")

    def test_title_survives_line_break_and_entity_without_double_escaping(self):
        titel = self.meta["titel"]
        self.assertNotIn("&amp;", titel)
        self.assertNotIn("<br", titel)
        self.assertNotIn("\xad", titel)
        self.assertEqual(self.meta["modul"], 2)

    def test_colophon_is_read(self):
        self.assertEqual(self.meta["app"], "1.0.6 (157)")
        self.assertEqual(self.meta["stand"], "9. August 2026")
        self.assertEqual(self.meta["beispielklasse"], "8a · Deutsch · 2 Schüler:innen")

    def test_chapters_are_collected_in_order(self):
        self.assertEqual(self.meta["kapitel"], [(1, "Erstes Kapitel"), (2, "Zweites Kapitel")])

    def test_figures_are_counted(self):
        self.assertEqual(self.meta["abbildungen"], 1)

    def test_cover_and_toc_are_dropped(self):
        self.assertNotIn('class="cover"', self.meta["body"])
        self.assertNotIn('class="toc"', self.meta["body"])
        self.assertNotIn("<svg", self.meta["body"])

    def test_chapter_headings_get_stable_anchors(self):
        self.assertIn('id="kapitel-1"', self.meta["body"])
        self.assertIn('id="kapitel-2"', self.meta["body"])

    def test_content_markup_survives_unchanged(self):
        for needle in ('class="figtitle"', 'class="sehen"', 'class="tun"', 'class="box warn"',
                       'class="ui"', "<table>"):
            self.assertIn(needle, self.meta["body"], needle)


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="hbtest-")
        os.makedirs(os.path.join(self.tmp, "assets"))
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "handbuch-web.py"), FIXTURE,
                            "--slug", "probe", "--modul", "2", "--root", self.tmp],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.out = r.stdout
        with open(os.path.join(self.tmp, "handbuch-probe.html"), encoding="utf-8") as f:
            self.page = f.read()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_webp_is_written_and_referenced(self):
        self.assertTrue(os.path.exists(
            os.path.join(self.tmp, "assets", "handbuch", "probe", "01-probe.webp")))
        self.assertIn('src="assets/handbuch/probe/01-probe.webp"', self.page)
        self.assertNotIn("screenshots/", self.page)

    def test_images_carry_dimensions_and_lazy_loading(self):
        img = re.search(r'<img[^>]*01-probe\.webp[^>]*>', self.page).group(0)
        self.assertIn('width="240"', img)
        self.assertIn('height="160"', img)
        self.assertIn('loading="lazy"', img)

    def test_page_carries_the_site_shell(self):
        self.assertIn('<div class="bar" id="bar">', self.page)
        self.assertIn("<footer>", self.page)
        self.assertIn("cloudflareinsights.com/beacon.min.js", self.page)

    def test_title_is_escaped_exactly_once_on_the_page(self):
        self.assertIn("Probe &amp; Muster", self.page)
        self.assertNotIn("&amp;amp;", self.page)

    def test_chapter_navigation_links_every_chapter(self):
        self.assertIn('href="#kapitel-1"', self.page)
        self.assertIn('href="#kapitel-2"', self.page)

    def test_handbook_css_is_scoped_to_avoid_collisions(self):
        """.lead, .box und .t heißen auf der Website schon etwas anderes — deshalb `.hb`."""
        self.assertIn('<article class="hb"', self.page)
        css = self.page.split("<style>", 1)[1].split("</style>", 1)[0]
        self.assertIn(".hb .box{", css)
        for regel in (".hb .lead{", ".hb .ui{", ".hb figcaption{"):
            self.assertIn(regel, css, regel)

    def test_warn_and_tip_boxes_use_design_tokens_not_raw_hex(self):
        """Farben nur über Tokens, sonst bricht der Dunkelmodus für diese eine Kante."""
        css = self.page.split("<style>", 1)[1].split("</style>", 1)[0]
        self.assertIn(".hb .box.warn{border-left-color:var(--hb-warn)}", css)
        self.assertIn(".hb .box.tip{border-left-color:var(--hb-tip)}", css)
        self.assertNotIn(".hb .box.warn{border-left-color:#", css)
        self.assertNotIn(".hb .box.tip{border-left-color:#", css)

    def test_summary_line_is_printed(self):
        self.assertIn("2 Kapitel", self.out)
        self.assertIn("1 Abbildungen", self.out)

    def test_rerun_produces_identical_output(self):
        first = self.page
        subprocess.run([sys.executable, os.path.join(TOOLS, "handbuch-web.py"), FIXTURE,
                        "--slug", "probe", "--modul", "2", "--root", self.tmp],
                       capture_output=True, text=True, check=True)
        with open(os.path.join(self.tmp, "handbuch-probe.html"), encoding="utf-8") as f:
            second = f.read()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
