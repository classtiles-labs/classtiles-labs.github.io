"""Tests für den KI-Kurs: Register, Generator und Seitenrahmen (tools/pages/ki_kurs.py).

Aufruf aus dem Repo-Wurzelverzeichnis:  python3 -m unittest discover -s tools/tests -v

Die Abbruchtests arbeiten mit einer Kopie der Fixture unter tools/tests/fixtures/kurs/, nicht mit
dem echten Register: Sie sollen den Generator prüfen, nicht den Stand der Inhalte.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(REPO, "tools", "pages"))

import ki_kurs  # noqa: E402

FIXTURE = os.path.join(REPO, "tools", "tests", "fixtures", "kurs")


class Kopie:
    """Kopie der Fixture in einem Temp-Ordner, die ein Test verändern darf."""

    def __enter__(self):
        self.tmp = tempfile.mkdtemp(prefix="kurstest-")
        shutil.copytree(FIXTURE, os.path.join(self.tmp, "kurs"))
        self.netz = os.path.join(self.tmp, "kurs", "netz.json")
        return self

    def __exit__(self, *a):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def aendere(self, f):
        with open(self.netz, encoding="utf-8") as fh:
            daten = json.load(fh)
        f(daten)
        with open(self.netz, "w", encoding="utf-8") as fh:
            json.dump(daten, fh)

    def fragment(self, sid, text):
        with open(os.path.join(self.tmp, "kurs", "stationen", f"{sid}.html"), "w",
                  encoding="utf-8") as fh:
            fh.write(text)


class TestRegister(unittest.TestCase):
    def test_doppelte_kennung_bricht_ab(self):
        with Kopie() as k:
            k.aendere(lambda d: d["stationen"].append(dict(d["stationen"][0])))
            with self.assertRaises(SystemExit):
                ki_kurs.lade_netz(k.netz)

    def test_unbekannte_linie_bricht_ab(self):
        with Kopie() as k:
            k.aendere(lambda d: d["stationen"][0].update(linie="Z"))
            with self.assertRaises(SystemExit):
                ki_kurs.lade_netz(k.netz)

    def test_umstieg_ins_leere_bricht_ab(self):
        with Kopie() as k:
            k.aendere(lambda d: d["stationen"][2].update(umstieg="gibt-es-nicht"))
            with self.assertRaises(SystemExit):
                ki_kurs.lade_netz(k.netz)

    def test_gebaut_ohne_fragment_bricht_ab(self):
        with Kopie() as k:
            k.aendere(lambda d: d["stationen"][1].update(status="gebaut", beschreibung="x"))
            with self.assertRaises(SystemExit):
                ki_kurs.lade_netz(k.netz)

    def test_gebaut_ohne_beschreibung_bricht_ab(self):
        with Kopie() as k:
            k.aendere(lambda d: d["stationen"][0].pop("beschreibung"))
            with self.assertRaises(SystemExit):
                ki_kurs.lade_netz(k.netz)

    def test_fragment_ohne_ticket_bricht_ab(self):
        with Kopie() as k:
            k.fragment("e-eins", '<section class="einordnung"><p>ohne Ticket</p></section>')
            with self.assertRaises(SystemExit):
                ki_kurs.lade_netz(k.netz)

    def test_zwei_tickets_brechen_ab(self):
        with Kopie() as k:
            k.fragment("e-eins", '<pre class="ticket-prompt">a</pre><pre class="ticket-prompt">b</pre>')
            with self.assertRaises(SystemExit):
                ki_kurs.lade_netz(k.netz)

    def test_fixture_ist_gueltig(self):
        netz = ki_kurs.lade_netz(os.path.join(FIXTURE, "netz.json"))
        self.assertEqual([s["id"] for s in netz["stationen"]], ["e-eins", "e-zwei", "e-drei", "a-eins"])


class TestSeiten(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seiten = ki_kurs.seiten(ki_kurs.lade_netz(os.path.join(FIXTURE, "netz.json")))

    def test_es_entstehen_uebersicht_und_gebaute_stationen(self):
        self.assertEqual(sorted(self.seiten), ["ki-kurs-a-eins.html", "ki-kurs-e-drei.html",
                                               "ki-kurs-e-eins.html", "ki-kurs.html"])

    def test_uebersicht_verlinkt_jede_gebaute_station_ohne_javascript(self):
        ueb = self.seiten["ki-kurs.html"]
        for sid in ("e-eins", "e-drei", "a-eins"):
            li = re.search(rf'<li[^>]*data-station="{sid}"[^>]*>(.*?)</li>', ueb, re.S)
            self.assertIsNotNone(li, sid)
            self.assertIn(f'href="ki-kurs-{sid}.html"', li.group(1))
        geplant = re.search(r'<li[^>]*data-station="e-zwei"[^>]*>(.*?)</li>', ueb, re.S).group(1)
        self.assertIn("in Planung", geplant)
        self.assertNotIn("href=", geplant)

    def test_uebersicht_traegt_slogan_und_marken(self):
        ueb = self.seiten["ki-kurs.html"]
        self.assertIn(f"<h1>{ki_kurs.SLOGAN}</h1>", ueb)
        for marke in ('id="liniennetz" hidden', 'id="fahrkarte"', 'id="fahrplan"',
                      'id="kurs-fortschritt"', 'id="kurs-netz"',
                      '<script type="module" src="assets/kurs/kurs.js"></script>',
                      '<link rel="stylesheet" href="assets/kurs/kurs.css">'):
            self.assertIn(marke, ueb)
        for l, name in (("E", "Einsteigen"), ("A", "Im Alltag"), ("B", "Selbst bauen")):
            self.assertIn(f'<ol class="kurs-liste" data-linie="{l}">', ueb)
            self.assertIn(name, ueb)

    def test_station_kennt_vorgaenger_und_nachfolger_auf_ihrer_linie(self):
        eins, drei, a = (self.seiten[f"ki-kurs-{s}.html"] for s in ("e-eins", "e-drei", "a-eins"))
        self.assertNotIn('rel="prev"', eins)
        self.assertIn('rel="next" href="ki-kurs-e-drei.html"', eins)  # geplante Station übersprungen
        self.assertIn('rel="prev" href="ki-kurs-e-eins.html"', drei)
        self.assertNotIn('rel="next"', drei)
        self.assertNotIn('rel="prev"', a)
        self.assertNotIn('rel="next"', a)

    def test_umstieg_wird_angeboten(self):
        drei = self.seiten["ki-kurs-e-drei.html"]
        self.assertIn('class="kurs-umstieg"', drei)
        self.assertIn('href="ki-kurs-a-eins.html"', drei)

    def test_station_kopf_nennt_linie_und_position(self):
        drei = self.seiten["ki-kurs-e-drei.html"]
        self.assertIn('<main class="station" data-station="e-drei" data-linie="E">', drei)
        self.assertIn("Station 3 von 3", drei)
        self.assertIn("Einsteigen", drei)

    def test_ticket_text_steht_im_html(self):
        self.assertIn("Prompt aus e-drei", self.seiten["ki-kurs-e-drei.html"])

    def test_register_steht_als_json_in_der_seite(self):
        m = re.search(r'<script type="application/json" id="kurs-netz">(.*?)</script>',
                      self.seiten["ki-kurs.html"], re.S)
        daten = json.loads(m.group(1))
        self.assertEqual(len(daten["stationen"]), 4)
        self.assertNotIn("fragment", daten["stationen"][0])


class TestEchteSeiten(unittest.TestCase):
    def test_echte_seiten_sind_auf_dem_stand(self):
        r = subprocess.run([sys.executable, os.path.join(REPO, "tools", "pages", "ki_kurs.py"),
                            "--check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
