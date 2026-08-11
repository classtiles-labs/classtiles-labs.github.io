"""Tests für coworkweb.py — das Claude-Heft aus gesetztem Druck-HTML.

Aufruf aus dem Repo-Wurzelverzeichnis:  python3 -m unittest discover -s tools/tests -v

Der Leser schneidet fremdes HTML zurecht, das niemand für ihn geschrieben hat. Ändert sich die
Quelle, soll er abbrechen und nicht eine halb geleerte Seite bauen — darauf zielen die Tests.
Die Bildwandlung wird mit `nur_struktur=True` umgangen, damit die Suite ohne cwebp läuft und
in Millisekunden bleibt.
"""
import os
import re
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(REPO, "tools", "pages"))

import coworkweb  # noqa: E402
import ki_handbuecher  # noqa: E402

PROBE = """<html><body>
<section class="cover">
  <p class="rubrik">Reihe · Heft 9</p>
  <h1 class="title">Ein Titel</h1>
  <p class="lede">Ein Claim</p>
  <p class="intro">Ein Anreißer.</p>
  <div class="foot"><p class="stand">Heft 9 · Stand: August 2026</p></div>
</section>
<section class="toc"><ul><li>weg damit</li></ul></section>
<section class="chapter" id="c01"><header class="op"><div class="opnum">01</div>
<h2>Worum es geht</h2></header><p>Erster Absatz.</p>
<div class="keep"><p>Zusammengehalten.</p>
<figure class="fig"><img src="data:image/png;base64,AAAA" alt="Bild 1">
<figcaption>Eine Bildunterschrift.</figcaption></figure></div></section>
<section class="chapter" id="c02"><header class="op"><div class="opnum">02</div>
<h2>Und weiter</h2></header><p>Zweiter Absatz.</p></section>
<section class="kolophon"><h1 class="secttl">Herkunft</h1>
<h2>Marken</h2><p>Ein Markenhinweis.</p></section>
</body></html>"""


def parse(text=PROBE, **kw):
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
        f.write(text)
        pfad = f.name
    try:
        return coworkweb.parse(pfad, "/nicht/benutzt", "assets/x", nur_struktur=True, **kw)
    finally:
        os.unlink(pfad)


class TestDeckblatt(unittest.TestCase):
    def test_felder(self):
        m = parse()
        self.assertEqual(m["titel"], "Ein Titel")
        self.assertEqual(m["claim"], "Ein Claim")
        self.assertEqual(m["stand"], "August 2026")
        self.assertEqual(m["ausgabe"], "Heft 9")
        self.assertIn("Ein Anreißer.", m["anreisser"])

    def test_deckblatt_und_inhaltsverzeichnis_entfallen(self):
        body = parse()["body"]
        self.assertNotIn("Ein Anreißer.", body)     # steht im Seitenkopf, nicht im Text
        self.assertNotIn("weg damit", body)

    def test_ohne_deckblatt_bricht_ab(self):
        with self.assertRaises(coworkweb.Fehler):
            parse(PROBE.replace('class="cover"', 'class="anders"'))

    def test_ohne_body_bricht_ab(self):
        with self.assertRaises(coworkweb.Fehler):
            parse("<html>kein body</html>")


class TestKapitel(unittest.TestCase):
    def test_anker_folgen_der_konvention_des_ki_bereichs(self):
        # Die Quelle nummeriert id="c01"; Glossar und Kurzfassungen erwarten kapitel-01.
        m = parse()
        self.assertEqual(m["kapitel"], [("01", "Worum es geht"), ("02", "Und weiter")])
        self.assertIn('<h2 class="chapter" id="kapitel-01">', m["body"])
        self.assertIn('<h2 class="chapter" id="kapitel-02">', m["body"])
        self.assertNotIn('id="c01"', m["body"])

    def test_kapitelnummer_steht_im_markup(self):
        self.assertIn('<span class="num">01</span>', parse()["body"])

    def test_ohne_kapitel_bricht_ab(self):
        with self.assertRaises(coworkweb.Fehler):
            parse(PROBE.replace('class="chapter"', 'class="anders"'))

    def test_keine_abschnittsanker(self):
        self.assertEqual(parse()["abschnitte"], [])


class TestAufraeumen(unittest.TestCase):
    def test_keep_wird_aufgeloest_der_inhalt_bleibt(self):
        body = parse()["body"]
        self.assertNotIn('class="keep"', body)
        self.assertIn("Zusammengehalten.", body)

    def test_keine_section_tags_mehr(self):
        self.assertNotIn("<section", parse()["body"])

    def test_kolophon_wird_ein_kasten_und_kein_kapitel(self):
        m = parse()
        self.assertIn('<div class="box kolophon">', m["body"])
        self.assertIn('<span class="t">Herkunft</span>', m["body"])
        self.assertIn("<p><b>Marken</b></p>", m["body"])
        self.assertNotIn("Herkunft", dict(m["kapitel"]).values())

    def test_offenes_keep_bricht_ab(self):
        with self.assertRaises(coworkweb.Fehler):
            coworkweb._keep_aufloesen('<div class="keep"><p>ohne Ende')

    def test_nur_struktur_entfernt_die_abbildungen(self):
        body = parse()["body"]
        self.assertNotIn("<figure", body)
        self.assertNotIn("base64", body)
        self.assertEqual(parse()["bilder"], 0)


class TestBilder(unittest.TestCase):
    """Diese Tests laufen mit echter Bildwandlung — deshalb ohne `nur_struktur`."""

    def mit_bildern(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8",
                                         delete=False) as f:
            f.write(text)
            pfad = f.name
        try:
            return coworkweb.parse(pfad, tempfile.mkdtemp(), "assets/x")
        finally:
            os.unlink(pfad)

    def test_quelle_ohne_bilder_bricht_ab(self):
        ohne = re.sub(r"<figure.*?</figure>", "", PROBE, flags=re.S)
        self.assertNotIn("<figure", ohne, "Vorbedingung des Tests stimmt nicht")
        with self.assertRaises(coworkweb.Fehler):
            self.mit_bildern(ohne)

    def test_unlesbare_bilddaten_melden_die_ursache(self):
        # „AAAA" ist gültiges Base64, aber kein PNG — genau der Fall, den eine geänderte
        # Quelle produzieren würde.
        with self.assertRaises(coworkweb.Fehler) as ctx:
            self.mit_bildern(PROBE)
        self.assertIn("Bild", str(ctx.exception))


class TestEchteQuelle(unittest.TestCase):
    def setUp(self):
        self.heft = next((b for b in ki_handbuecher.BAENDE if b.get("format") == "html"), None)
        if not self.heft or not os.path.exists(os.path.join(REPO, self.heft["quelle"])):
            self.skipTest("Quelle des Hefts nicht vorhanden")

    def test_heft_laesst_sich_lesen(self):
        m = ki_handbuecher.lies(self.heft, nur_struktur=True)
        self.assertEqual(len(m["kapitel"]), 12)
        self.assertEqual(m["stand"], "August 2026")
        self.assertTrue(m["titel"])
        self.assertNotIn("base64", m["body"])

    def test_gebaute_seite_traegt_die_bilder_als_dateien(self):
        seite = os.path.join(REPO, "ki-handbuch-cowork.html")
        if not os.path.exists(seite):
            self.skipTest("Seite noch nicht gebaut")
        with open(seite, encoding="utf-8") as f:
            html = f.read()
        self.assertEqual(html.count("assets/ki/cowork/bild-"), 17)
        for nr in range(1, 18):
            self.assertTrue(
                os.path.exists(os.path.join(REPO, "assets", "ki", "cowork", f"bild-{nr:02d}.webp")),
                f"bild-{nr:02d}.webp fehlt")


if __name__ == "__main__":
    unittest.main()
