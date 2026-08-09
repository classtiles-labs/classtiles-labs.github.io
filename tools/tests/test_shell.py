"""Tests für shell.py und apply-shell.py.

Aufruf aus dem Repo-Wurzelverzeichnis:  python3 -m unittest discover -s tools/tests -v
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))

import shell  # noqa: E402

BAR = re.compile(r'<div class="bar" id="bar">.*?\n  </div>', re.S)
FOOTER = re.compile(r'<footer>.*?</footer>', re.S)


def pages(root):
    out = []
    for name in sorted(os.listdir(root)):
        if name.endswith(".html"):
            out.append(name)
    endir = os.path.join(root, "en")
    if os.path.isdir(endir):
        for name in sorted(os.listdir(endir)):
            if name.endswith(".html"):
                out.append("en/" + name)
    return out


class TestShellFacts(unittest.TestCase):
    def test_lang_of(self):
        self.assertEqual(shell.lang_of("index.html"), "de")
        self.assertEqual(shell.lang_of("modul-gruppen.html"), "de")
        self.assertEqual(shell.lang_of("en/index.html"), "en")

    def test_twin_of_pairs_both_ways(self):
        self.assertEqual(shell.twin_of("datenschutz.html"), "en/privacy.html")
        self.assertEqual(shell.twin_of("en/privacy.html"), "../datenschutz.html")
        self.assertEqual(shell.twin_of("index.html"), "en/index.html")
        self.assertEqual(shell.twin_of("en/index.html"), "../index.html")

    def test_active_of(self):
        self.assertEqual(shell.active_of("support.html"), "support.html")
        self.assertEqual(shell.active_of("modul-kalender.html"), "index.html#module")
        self.assertIsNone(shell.active_of("impressum.html"))

    def test_bar_contains_instagram_and_language_switch(self):
        bar = shell.bar_block("index.html")
        self.assertIn('href="https://www.instagram.com/classtiles/"', bar)
        self.assertIn('class="lang"', bar)
        self.assertIn('href="en/index.html"', bar)

    def test_script_block_carries_the_cloudflare_beacon(self):
        self.assertIn("cloudflareinsights.com/beacon.min.js", shell.script_block())


class TestApplyShell(unittest.TestCase):
    """apply-shell.py schreibt die Shell zurück — und darf dabei nichts anderes anfassen."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="shelltest-")
        for name in pages(REPO):
            dst = os.path.join(self.tmp, name)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(REPO, name), dst)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_apply(self):
        r = subprocess.run([sys.executable, os.path.join(REPO, "tools", "apply-shell.py"),
                            "--root", self.tmp],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def read(self, name):
        return open(os.path.join(self.tmp, name), encoding="utf-8").read()

    def test_bar_and_footer_are_reproduced_byte_for_byte(self):
        before = {n: self.read(n) for n in pages(self.tmp)}
        self.run_apply()
        for name, old in before.items():
            new = self.read(name)
            self.assertEqual(BAR.search(old).group(0), BAR.search(new).group(0),
                             f"Kopfleiste von {name} hat sich geändert")
            self.assertEqual(FOOTER.search(old).group(0), FOOTER.search(new).group(0),
                             f"Fußzeile von {name} hat sich geändert")

    def test_body_content_is_untouched(self):
        """Alles zwischen Kopfleiste und Fußzeile bleibt, wie es war."""
        def middle(t):
            return t[BAR.search(t).end():FOOTER.search(t).start()]
        before = {n: middle(self.read(n)) for n in pages(self.tmp)}
        self.run_apply()
        for name, old in before.items():
            self.assertEqual(old, middle(self.read(name)), f"Inhalt von {name} hat sich geändert")

    def test_css_is_identical_on_every_page(self):
        self.run_apply()
        seen = {re.search(r'<style>(.*?)</style>', self.read(n), re.S).group(1)
                for n in pages(self.tmp)}
        self.assertEqual(len(seen), 1, "Es gibt mehr als eine CSS-Fassung")

    def test_second_run_changes_nothing(self):
        self.run_apply()
        after_first = {n: self.read(n) for n in pages(self.tmp)}
        out = self.run_apply()
        for name, text in after_first.items():
            self.assertEqual(text, self.read(name), f"{name} wurde im zweiten Lauf verändert")
        self.assertIn("0 geändert", out)


if __name__ == "__main__":
    unittest.main()
