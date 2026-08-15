"""Tests für die Generatoren des KI-Bereichs: Glossar, Kurzfassungen, Neues.

Aufruf aus dem Repo-Wurzelverzeichnis:  python3 -m unittest discover -s tools/tests -v

Der Schwerpunkt liegt auf den Abbruchbedingungen. Alle drei Generatoren schreiben Links, die
sie selbst nicht prüfen können, wenn sie es nicht ausdrücklich tun — ein Glossareintrag auf
einen umbenannten Anker, ein „weiter"-Ziel auf eine gelöschte Seite. Diese Tests stellen
sicher, dass so etwas den Lauf beendet, statt einen toten Link zu erzeugen.
"""
import os
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(REPO, "tools", "pages"))

import handbuchtext  # noqa: E402
import ki_glossar  # noqa: E402
import ki_handbuecher  # noqa: E402
import ki_kurzfassungen  # noqa: E402
import ki_neues  # noqa: E402


def quellen_da():
    return all(os.path.exists(os.path.join(REPO, b["quelle"]))
               for b in ki_handbuecher.BAENDE if b["quelle"])


def markdown_baende():
    """Die fünf Bände aus Markdown — ohne das Cowork-Heft, dessen Quelle HTML ist."""
    return [b for b in ki_handbuecher.BAENDE
            if b["quelle"] and b.get("format") != "html"]


def kurzfassungs_baende():
    """Bände mit Kurzfassung. Das Heft hat keine — siehe ki_kurzfassungen.main()."""
    return [b for b in ki_handbuecher.BAENDE if b.get("kurz_minuten")]


class TestGlossar(unittest.TestCase):
    def setUp(self):
        if not quellen_da():
            self.skipTest("Quellen des Nachbarrepos nicht vorhanden")
        self.sicherung = [dict(g) for g in ki_glossar.GLOSSAR]

    def tearDown(self):
        ki_glossar.GLOSSAR[:] = self.sicherung

    def test_alle_ziele_loesen_auf(self):
        ki_glossar.seite()          # wirft SystemExit, sobald ein Anker fehlt

    def test_jeder_eintrag_hat_mindestens_ein_ziel(self):
        for g in ki_glossar.GLOSSAR:
            with self.subTest(begriff=g["begriff"]):
                self.assertTrue(g["ziele"], "Eintrag ohne Beleg")

    def test_begriffe_sind_eindeutig(self):
        begriffe = [g["begriff"] for g in ki_glossar.GLOSSAR]
        self.assertCountEqual(begriffe, set(begriffe))

    def test_unbekannter_anker_bricht_ab(self):
        ki_glossar.GLOSSAR[0] = dict(ki_glossar.GLOSSAR[0],
                                     ziele=[("workflows", "kapitel-99-gibt-es-nicht")])
        with self.assertRaises(SystemExit):
            ki_glossar.seite()

    def test_querverweis_ins_leere_bricht_ab(self):
        ki_glossar.GLOSSAR[0] = dict(ki_glossar.GLOSSAR[0], auch="Erfundener Begriff")
        with self.assertRaises(SystemExit):
            ki_glossar.seite()


class TestKurzfassungen(unittest.TestCase):
    def setUp(self):
        if not quellen_da():
            self.skipTest("Quellen des Nachbarrepos nicht vorhanden")

    def test_abschnitt_schneidet_bis_zur_naechsten_ueberschrift(self):
        body = '<h3 id="a">A</h3><p>eins</p><ul><li>x</li></ul><h3 id="b">B</h3><p>zwei</p>'
        self.assertEqual(ki_kurzfassungen.abschnitt(body, "a", "probe"),
                         "<p>eins</p><ul><li>x</li></ul>")

    def test_abschnitt_am_ende_des_dokuments(self):
        self.assertEqual(ki_kurzfassungen.abschnitt('<h3 id="z">Z</h3><p>letzt</p>', "z", "p"),
                         "<p>letzt</p>")

    def test_fehlender_abschnitt_bricht_ab(self):
        with self.assertRaises(SystemExit):
            ki_kurzfassungen.abschnitt('<h3 id="a">A</h3><p>x</p>', "gibtsnicht", "probe")

    def test_kolophon_am_dokumentende_faellt_weg(self):
        body = ('<h3 id="idee">Die Idee</h3><p>Der Satz.</p>'
                "<p><b>Band 3 · Ausgabe 1 · Redaktionsstand: 10. August 2026</b></p>")
        self.assertEqual(ki_kurzfassungen.abschnitt(body, "idee", "probe"), "<p>Der Satz.</p>")

    def test_kein_band_zeigt_das_kolophon_in_der_kurzfassung(self):
        for b in kurzfassungs_baende():
            with self.subTest(band=b["slug"]):
                m = handbuchtext.parse(os.path.join(REPO, b["quelle"]))
                idee = ki_kurzfassungen.abschnitt(m["body"],
                                                  ki_kurzfassungen.KURZ[b["slug"]]["idee"][1],
                                                  b["slug"])
                self.assertNotIn("Redaktionsstand", idee)
                self.assertNotIn("Ausgabe", idee)

    def test_jeder_markdown_band_hat_eine_kurzfassung(self):
        for b in markdown_baende():
            with self.subTest(band=b["slug"]):
                self.assertIn(b["slug"], ki_kurzfassungen.KURZ)
                self.assertIn("kurz_minuten", b)

    def test_das_heft_hat_bewusst_keine(self):
        heft = [b for b in ki_handbuecher.BAENDE if b.get("format") == "html"]
        self.assertTrue(heft, "kein HTML-Titel mehr in BAENDE — Test anpassen")
        for b in heft:
            self.assertNotIn("kurz_minuten", b)
            self.assertNotIn(b["slug"], ki_kurzfassungen.KURZ)

    def test_alle_belege_zeigen_auf_vorhandene_anker(self):
        for b in kurzfassungs_baende():
            m = handbuchtext.parse(os.path.join(REPO, b["quelle"]))
            vorhanden = {f"kapitel-{nr}" for nr, _ in m["kapitel"]}
            vorhanden |= {a for _, _, a in m["abschnitte"]}
            k = ki_kurzfassungen.KURZ[b["slug"]]
            for anker in [k["idee"][1], k["methode"][1], k["grenzen"][1]]:
                with self.subTest(band=b["slug"], anker=anker):
                    self.assertIn(anker, vorhanden)
            for text, anker in k["mitnehmen"]:
                if anker:
                    with self.subTest(band=b["slug"], anker=anker):
                        self.assertIn(anker, vorhanden, f"Beleg für {text[:40]!r}")


class TestNeues(unittest.TestCase):
    """Das Eintragsformat wird von Hand geschrieben — hier zählt die Fehlermeldung."""

    KOPF = ("---\ntitel: Ein Titel\nart: Tipp\nweiter:\n"
            "  - Zu den Handbüchern | ki-handbuecher.html\n---\nEin Absatz.\n")

    def eintrag(self, text, name="2026-08-11-eine-kennung.md"):
        alt = ki_neues.QUELLE
        ordner = tempfile.mkdtemp()
        ki_neues.QUELLE = ordner
        try:
            with open(os.path.join(ordner, name), "w", encoding="utf-8") as f:
                f.write(text)
            return ki_neues.lies(name)
        finally:
            ki_neues.QUELLE = alt

    def test_kopf_und_text(self):
        e = self.eintrag(self.KOPF)
        self.assertEqual(e["titel"], "Ein Titel")
        self.assertEqual(e["art"], "Tipp")
        self.assertEqual(e["datum"], "11. August 2026")
        self.assertEqual(e["kennung"], "2026-08-11-eine-kennung")
        self.assertEqual(e["weiter"], [("Zu den Handbüchern", "ki-handbuecher.html")])
        self.assertIn("<p>Ein Absatz.</p>", e["text"])

    def test_datum_kommt_aus_dem_dateinamen(self):
        e = self.eintrag(self.KOPF, "2025-01-02-neujahr.md")
        self.assertEqual(e["datum"], "2. Januar 2025")
        self.assertEqual(e["jahr"], "2025")

    def test_falscher_dateiname_bricht_ab(self):
        with self.assertRaises(SystemExit):
            self.eintrag(self.KOPF, "ohne-datum.md")

    def test_fehlender_titel_bricht_ab(self):
        with self.assertRaises(SystemExit):
            self.eintrag("---\nart: Tipp\n---\nText.\n")

    def test_unbekannte_art_bricht_ab(self):
        with self.assertRaises(SystemExit):
            self.eintrag("---\ntitel: T\nart: Geplauder\n---\nText.\n")

    def test_fehlender_kopf_bricht_ab(self):
        with self.assertRaises(SystemExit):
            self.eintrag("Nur Text, kein Kopf.\n")

    def test_weiter_ohne_ziel_bricht_ab(self):
        with self.assertRaises(SystemExit):
            self.eintrag("---\ntitel: T\nart: Neu\nweiter:\n  - Nur Text\n---\nText.\n")

    def test_weiter_auf_fehlende_seite_bricht_ab(self):
        with self.assertRaises(SystemExit):
            self.eintrag("---\ntitel: T\nart: Neu\nweiter:\n"
                         "  - Weg | gibt-es-nicht.html\n---\nText.\n")

    def test_weiter_mit_anker_wird_akzeptiert(self):
        e = self.eintrag("---\ntitel: T\nart: Neu\nweiter:\n"
                         "  - Kapitel | ki-handbuch-workflows.html#kapitel-04\n---\nText.\n")
        self.assertEqual(e["weiter"][0][1], "ki-handbuch-workflows.html#kapitel-04")

    def test_echte_eintraege_lassen_sich_lesen(self):
        namen = sorted(n for n in os.listdir(ki_neues.QUELLE) if n.endswith(".md"))
        self.assertTrue(namen, "keine Einträge unter inhalt/neues/")
        for n in namen:
            with self.subTest(eintrag=n):
                self.assertTrue(ki_neues.lies(n)["text"].strip())

    def test_neueste_zuerst(self):
        e = [dict(sortier=("2026", "01", "05")), dict(sortier=("2026", "08", "11")),
             dict(sortier=("2025", "12", "31"))]
        sortiert = sorted(e, key=lambda x: x["sortier"], reverse=True)
        self.assertEqual([x["sortier"][1] for x in sortiert], ["08", "01", "12"])


if __name__ == "__main__":
    unittest.main()
