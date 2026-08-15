"""Tests für handbuchtext.py — die Markdown-Grammatik der KI-Handbücher.

Aufruf aus dem Repo-Wurzelverzeichnis:  python3 -m unittest discover -s tools/tests -v

Die Anker sind eine öffentliche Schnittstelle (das Glossar verlinkt sie), deshalb prüfen die
Ankertests exakte Zeichenketten und nicht nur „irgendein Anker ist da".
"""
import os
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))

import handbuchtext as ht  # noqa: E402

KOPF = """# Probehandbuch

## Ein Claim.

**Band 9 des Praxis-Handbuchs**

Ein Vorlauftext.

> Der Merksatz.

Band 9 · Ausgabe 1 · Stand: 1. Januar 2026

"""


def parse(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as f:
        f.write(KOPF + text)
        pfad = f.name
    try:
        return ht.parse(pfad)
    finally:
        os.unlink(pfad)


class TestSlug(unittest.TestCase):
    def test_umlaute_werden_umschrieben(self):
        self.assertEqual(ht.slug("Größe für Lehrkräfte"), "groesse-fuer-lehrkraefte")

    def test_fuehrende_zaehlnummer_entfaellt(self):
        self.assertEqual(ht.slug("1 · Prompt"), "prompt")
        self.assertEqual(ht.slug("12 · Der Kontextfilter"), "der-kontextfilter")

    def test_laenge_ist_begrenzt(self):
        lang = ht.slug("Ankerdatei · der Rahmen der immer und überall für alle gilt")
        self.assertEqual(lang.count("-"), ht.ANKER_WOERTER - 1)


class TestInline(unittest.TestCase):
    def test_auszeichnungen(self):
        self.assertEqual(ht.inline("**fett**"), "<b>fett</b>")
        self.assertEqual(ht.inline("*kursiv*"), "<em>kursiv</em>")
        self.assertEqual(ht.inline("`code`"), "<code>code</code>")
        self.assertEqual(ht.inline("[t](ziel.html)"), '<a href="ziel.html">t</a>')

    def test_html_wird_zuerst_escaped(self):
        self.assertEqual(ht.inline("a < b & c"), "a &lt; b &amp; c")
        self.assertEqual(ht.inline("**<b>**"), "<b>&lt;b&gt;</b>")


class TestBloecke(unittest.TestCase):
    def test_auszeichnung_ueber_zeilenumbruch(self):
        # Die Quelle bricht bei ~95 Zeichen um; zeilenweises Auszeichnen ließe das Markdown stehen.
        m = parse("# 01 · Kapitel\n\n**Band 2 — Unterrichtsmaterial\nselbst bauen**\n")
        self.assertIn("<b>Band 2 — Unterrichtsmaterial selbst bauen</b>", m["body"])
        self.assertNotIn("**", m["body"])

    def test_harter_umbruch_bei_zwei_leerzeichen(self):
        m = parse("# 01 · Kapitel\n\nErste Zeile.  \nZweite Zeile.\n")
        self.assertIn("Erste Zeile.<br>Zweite Zeile.", m["body"])

    def test_tabelle(self):
        m = parse("# 01 · Kapitel\n\n| A | B |\n|---|---|\n| 1 | 2 |\n")
        self.assertIn('<div class="tablewrap"><table><thead><tr><th>A</th><th>B</th></tr>'
                      "</thead><tbody><tr><td>1</td><td>2</td></tr></tbody></table></div>",
                      m["body"])

    def test_tabelle_ohne_trennzeile_bricht_ab(self):
        with self.assertRaises(ht.Fehler):
            parse("# 01 · Kapitel\n\n| A | B |\n| 1 | 2 |\n")

    def test_listen(self):
        m = parse("# 01 · Kapitel\n\n- eins\n- zwei\n\n1. a\n2. b\n")
        self.assertIn("<ul><li>eins</li><li>zwei</li></ul>", m["body"])
        self.assertIn("<ol><li>a</li><li>b</li></ol>", m["body"])

    def test_umbrochener_listenpunkt_bleibt_ein_punkt(self):
        m = parse("# 01 · Kapitel\n\n- ein sehr langer Punkt,\n  der umbricht\n- zwei\n")
        self.assertIn("<li>ein sehr langer Punkt, der umbricht</li>", m["body"])

    def test_promptblock_bleibt_woertlich(self):
        m = parse("# 01 · Kapitel\n\n~~~text\nSchreibe <fünf> Fragen.\n  Eingerückt.\n~~~\n")
        self.assertIn('<pre class="prompt">Schreibe &lt;fünf&gt; Fragen.\n  Eingerückt.</pre>',
                      m["body"])

    def test_offener_promptblock_bricht_ab(self):
        with self.assertRaises(ht.Fehler):
            parse("# 01 · Kapitel\n\n~~~text\nohne Ende\n")

    def test_merksatz_wird_blockquote(self):
        m = parse("# 01 · Kapitel\n\n> Ein Arbeitsauftrag.\n> Kein Suchbegriff.\n")
        self.assertIn("<blockquote>Ein Arbeitsauftrag. Kein Suchbegriff.</blockquote>", m["body"])


class TestAnker(unittest.TestCase):
    def test_kapitel_und_abschnittsanker(self):
        m = parse("# 00 · Die sechs Begriffe\n\n## 1 · Prompt\n\nText.\n")
        self.assertIn('<h2 class="chapter" id="kapitel-00">', m["body"])
        self.assertIn('<h3 id="kapitel-00-prompt">', m["body"])

    def test_gleicher_abschnitt_in_zwei_kapiteln_kollidiert_nicht(self):
        # „## Die Grenze" steht am Ende jedes Kapitels — der Anker trägt deshalb die Kapitelnummer.
        m = parse("# 00 · Eins\n\n## Die Grenze\n\nA.\n\n# 01 · Zwei\n\n## Die Grenze\n\nB.\n")
        self.assertIn('id="kapitel-00-die-grenze"', m["body"])
        self.assertIn('id="kapitel-01-die-grenze"', m["body"])

    def test_doppelter_anker_im_selben_kapitel_bricht_ab(self):
        with self.assertRaises(ht.Fehler):
            parse("# 00 · Eins\n\n## Die Grenze\n\nA.\n\n## Die Grenze\n\nB.\n")

    def test_abschnitte_werden_mit_kapitelnummer_gemeldet(self):
        m = parse("# 03 · Kapitel\n\n## 1 · Prompt\n\nText.\n")
        self.assertIn(("03", "1 · Prompt", "kapitel-03-prompt"), m["abschnitte"])


class TestVorspann(unittest.TestCase):
    def test_felder(self):
        m = parse("# 01 · Kapitel\n\nText.\n")
        self.assertEqual(m["titel"], "Probehandbuch")
        self.assertEqual(m["claim"], "Ein Claim.")
        self.assertEqual(m["stand"], "1. Januar 2026")
        self.assertEqual(m["ausgabe"], "Band 9 · Ausgabe 1")
        self.assertEqual(m["merksatz"], "Der Merksatz.")
        self.assertIn("Ein Vorlauftext.", m["anreisser"])

    def test_standzeile_steht_nicht_im_anreisser(self):
        m = parse("# 01 · Kapitel\n\nText.\n")
        self.assertNotIn("Stand:", m["anreisser"])
        self.assertNotIn("Der Merksatz.", m["anreisser"])

    def test_ohne_kapitel_bricht_ab(self):
        with self.assertRaises(ht.Fehler):
            parse("Nur Vorspann, kein Kapitel.\n")


class TestEchteQuellen(unittest.TestCase):
    """Die fünf Bände selbst — sie liegen im Nachbarrepo und fehlen ggf. auf anderen Rechnern."""

    def setUp(self):
        sys.path.insert(0, os.path.join(REPO, "tools", "pages"))
        import ki_handbuecher  # noqa: E402
        self.baende = ki_handbuecher.BAENDE
        # Das Cowork-Heft hat eine HTML-Quelle und wird von tools/coworkweb.py gelesen —
        # hier geht es nur um die Markdown-Bände.
        vorhanden = [b for b in self.baende
                     if b["quelle"] and b.get("format") != "html"
                     and os.path.exists(os.path.join(REPO, b["quelle"]))]
        if not vorhanden:
            self.skipTest("Quellen des Nachbarrepos nicht vorhanden")
        self.vorhanden = vorhanden

    def test_alle_baende_lassen_sich_lesen(self):
        for b in self.vorhanden:
            with self.subTest(band=b["slug"]):
                m = ht.parse(os.path.join(REPO, b["quelle"]))
                self.assertTrue(m["kapitel"], "kein Kapitel gefunden")
                self.assertTrue(m["stand"])

    def test_kein_unkonvertiertes_markdown(self):
        import re
        for b in self.vorhanden:
            with self.subTest(band=b["slug"]):
                body = ht.parse(os.path.join(REPO, b["quelle"]))["body"]
                ohne_pre = re.sub(r"<pre.*?</pre>", "", body, flags=re.S)
                self.assertNotIn("**", ohne_pre)
                self.assertNotIn("~~~", ohne_pre)
                self.assertEqual(re.findall(r"(?<![*\w])\*(?![*\s])", ohne_pre), [])


if __name__ == "__main__":
    unittest.main()
