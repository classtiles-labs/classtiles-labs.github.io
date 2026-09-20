"""Prüft, ob der Notenschlüssel-Rechner richtig rechnet — indem sein Skript ausgeführt wird.

Aufruf aus dem Repo-Wurzelverzeichnis:  python3 -m unittest discover -s tools/tests -v

Die Rechenfunktionen werden aus notenschluessel-rechner.html herausgelöst und mit Node
ausgeführt. Das ist die einzige Stelle im Repo, die mehr als python3 braucht — deshalb
**überspringt** sich der Test, wenn kein Node da ist, statt den Lauf rot zu machen. Der
Grundsatz „der gesamte Bau ist python3 ohne Abhängigkeit" bleibt damit unberührt.

Eine Nachbildung der Formel in Python wäre keine Prüfung: Sie würde die erwartete Antwort in
den Test hineinreichen und bei jedem Denkfehler genauso falsch rechnen wie die Seite.
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
SEITE = os.path.join(REPO, "notenschluessel-rechner.html")

SKRIPT = re.compile(r'<script(?![^>]*ld\+json)[^>]*>(.*?)</script>', re.S)

# Was ausgeführt wird: der Rechenteil des Seitenskripts. Die Seite trennt ihn selbst durch
# eine Marke vom Anzeigeteil ab — daran hängt diese Prüfung.
VON, MARKE = "const CT_1_6", "// ---- Anzeige ----"

# Die Prüfungen laufen in Node und melden sich als JSON zurück.
PRUEFUNG = r'''
const raus = [];
const ist = (was, a, b) => raus.push([was, JSON.stringify(a), JSON.stringify(b)]);

// Linear mit Sockel: der Abstand Sockel…100 wird geviertelt, darunter 5 bis zum halben
// Sockelwert. Sockel 50 ergibt damit die verbreitete Tabelle 87,5 / 75 / 62,5 / 50 / 25.
ist("linear(50)", linear(50).map(x => x[0]), [87.5, 75, 62.5, 50, 25, 0]);
ist("linear(40)", linear(40).map(x => x[0]), [85, 70, 55, 40, 20, 0]);
ist("linear(60)", linear(60).map(x => x[0]), [90, 80, 70, 60, 30, 0]);

// Punkte aus Prozent, im gewählten Raster aufgerundet.
ist("4 ab 50% von 60", abPunkten(50, 60, 0.5), 30);
ist("1 ab 87,5% von 60", abPunkten(87.5, 60, 0.5), 52.5);
ist("0% ergibt 0 Punkte", abPunkten(0, 60, 0.5), 0);
ist("aufrunden ins Raster", abPunkten(50, 7, 1), 4);

// Die Gleitkomma-Kante, wegen der die Toleranz in abPunkten steht. 81 % von 75 Punkten sind
// exakt 60,75 — geteilt durch das Raster 0,25 rechnet das aber als 243,00000000000003, und
// ein Aufrunden ohne Toleranz verlangt 61 Punkte. Wer genau 81 % schreibt, bekäme damit eine
// Note zu wenig. Geprüft wird hier die Funktion selbst, nicht die Formel nachgebaut.
ist("81 % von 75 P., Raster 0,25", abPunkten(81, 75, 0.25), 60.75);
ist("81 % von 150 P., Raster 0,5", abPunkten(81, 150, 0.5), 121.5);
ist("55 % von 50 P., Raster 0,5", abPunkten(55, 50, 0.5), 27.5);
ist("67 % von 70 P., Raster 0,1", Math.round(abPunkten(67, 70, 0.1) * 100) / 100, 46.9);

// Die drei Tabellen aus der App.
ist("1-6", CT_1_6.map(x => x[0]), [92, 81, 67, 50, 30, 0]);
ist("1-6 Noten", CT_1_6.map(x => x[1]), ["1", "2", "3", "4", "5", "6"]);
ist("1-6 mit Tendenzen: 17 Stufen", CT_1_6_PM.length, 17);
ist("Oberstufe: 16 Stufen", CT_0_15.length, 16);
ist("Oberstufe: 15 Punkte ab 95%", CT_0_15[0], [95, "15"]);

// Tendenzen: jedes Band gedrittelt, das oberste bis 100 %, das unterste ohne Tendenz.
const tend = mitTendenzen(linear(50));
ist("1+ ab", Math.round(tend[0][0] * 1000) / 1000, 95.833);
ist("1 ab", Math.round(tend[1][0] * 1000) / 1000, 91.667);
ist("1- ab", tend[2][0], 87.5);
ist("unterste Stufe ohne Tendenz", tend[tend.length - 1], [0, "6"]);
ist("5 Bänder gedrittelt plus die 6", tend.length, 16);

// Jede Tabelle muss streng fallen und bei 0 enden, sonst findet die Suche die falsche Stufe
// oder gar keine.
for (const [name, tab] of [["1-6", CT_1_6], ["1-6 pm", CT_1_6_PM], ["0-15", CT_0_15],
                           ["linear", linear(50)], ["linear+tend", tend],
                           ["linear(33)", linear(33)], ["tend(33)", mitTendenzen(linear(33))]]) {
  ist(name + " faellt streng", tab.every((x, i) => i === 0 || tab[i - 1][0] > x[0]), true);
  ist(name + " endet bei 0", tab[tab.length - 1][0], 0);
}
console.log(JSON.stringify(raus));
'''


def rechenkern():
    with open(SEITE, encoding="utf-8") as f:
        text = f.read()
    js = next(s for s in SKRIPT.findall(text) if VON in s)
    return js[js.index(VON):js.index(MARKE)]


@unittest.skipUnless(shutil.which("node"), "Node nicht vorhanden — Rechnerprüfung übersprungen")
class TestRechenkern(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory(prefix="rechner-") as tmp:
            datei = os.path.join(tmp, "pruefung.mjs")
            with open(datei, "w", encoding="utf-8") as f:
                f.write(rechenkern() + PRUEFUNG)
            r = subprocess.run([shutil.which("node"), datei],
                               capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError(f"Das Rechnerskript läuft nicht: {r.stderr.strip()}")
        cls.ergebnisse = json.loads(r.stdout)

    def test_die_seite_rechnet_wie_erwartet(self):
        abweichungen = [(was, ist, soll) for was, ist, soll in self.ergebnisse if ist != soll]
        self.assertEqual(abweichungen, [],
                         "\n".join(f"{was}: {ist} statt {soll}"
                                   for was, ist, soll in abweichungen))

    def test_es_wurde_wirklich_geprueft(self):
        """Ein leeres Ergebnis wäre grün, ohne etwas geprüft zu haben."""
        self.assertGreaterEqual(len(self.ergebnisse), 25)


class TestRechenkernHerausloesen(unittest.TestCase):
    """Verschiebt sich der Aufbau der Seite, muss das auffallen — sonst prüft der Test oben
    irgendwann ein leeres Stück Text und bleibt trotzdem grün."""

    def test_der_kern_enthaelt_die_erwarteten_funktionen(self):
        kern = rechenkern()
        for name in ("CT_1_6", "CT_1_6_PM", "CT_0_15", "function linear",
                     "function mitTendenzen", "function abPunkten"):
            self.assertIn(name, kern, f"{name} fehlt im herausgelösten Rechenkern")
        self.assertNotIn("document", kern, "Der Kern greift auf den DOM zu")


if __name__ == "__main__":
    sys.exit(unittest.main())
