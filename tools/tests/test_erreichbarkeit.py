"""Prüft, ob jede Seite gefunden werden kann — von Besuchern und von Google.

Aufruf aus dem Repo-Wurzelverzeichnis:  python3 -m unittest discover -s tools/tests -v

Entstanden aus einem Fehler: Der Notenschlüssel-Rechner wurde gebaut, um aus der Suche
gefunden zu werden, hing danach aber an einem einzigen Verweis als letzter Aufzählungspunkt
tief in der Modulseite. Für Leser unauffindbar, und für Google eine Seite ohne internes
Gewicht — schlecht erreichbare Seiten werden seltener besucht und schlechter bewertet.
`check-links.py` fand daran nichts auszusetzen: Es prüft, ob Verweise ins Leere gehen, nicht,
ob eine Seite genug davon abbekommt.

Zwei Maße, beide aus dem fertigen HTML gerechnet, nicht aus einer gepflegten Liste:

* **eingehende Verweise** — wie oft überhaupt auf eine Seite gezeigt wird.
* **Klicktiefe** — wie viele Klicks sie von der Startseite entfernt liegt.
"""
import collections
import os
import re
import sys
import unittest
from urllib.parse import unquote, urldefrag

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))

import shell  # noqa: E402

START = "index.html"

# Die KI-Bände liegen am tiefsten: Startseite → Digitalisierung & KI → Handbücher → Band.
# Drei Klicks sind vertretbar; vier wären ein Zeichen, dass ein Bereich abrutscht.
MAX_TIEFE = 3

# Die beiden Seiten, die Besucher aus der Suche erreichen sollen. Sie gehören in die Fußzeile
# oder die Kopfleiste und damit einen Klick von überall entfernt — genau das war der Fehler.
SUCHEINGAENGE = ("notenschluessel-rechner.html", "preise.html")


def _seiten():
    return shell.pages(REPO)


def _inhalt():
    return {p: open(os.path.join(REPO, p), encoding="utf-8").read() for p in _seiten()}


def _ziele(seite, inhalt):
    """Interne Seitenverweise dieser Seite, als Repo-Pfade."""
    out = set()
    for url in re.findall(r'href="([^"]*)"', inhalt[seite]):
        if not url or url.startswith(("mailto:", "data:", "http://", "https://", "#")):
            continue
        ziel, _ = urldefrag(unquote(url))
        if not ziel:
            continue
        rel = os.path.normpath(os.path.join(os.path.dirname(seite), ziel))
        if rel in inhalt:
            out.add(rel)
    return out


class TestErreichbarkeit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.inhalt = _inhalt()
        cls.eingehend = collections.Counter()
        for seite in cls.inhalt:
            for ziel in _ziele(seite, cls.inhalt):
                if ziel != seite:
                    cls.eingehend[ziel] += 1

        cls.tiefe = {START: 0}
        warteschlange = collections.deque([START])
        while warteschlange:
            seite = warteschlange.popleft()
            for ziel in _ziele(seite, cls.inhalt):
                if ziel not in cls.tiefe:
                    cls.tiefe[ziel] = cls.tiefe[seite] + 1
                    warteschlange.append(ziel)

    def test_keine_seite_ist_verwaist(self):
        """Auf jede Seite zeigt mindestens eine andere. Eine Seite ohne eingehenden Verweis
        existiert für Google praktisch nicht, auch wenn sie in der Sitemap steht."""
        verwaist = [p for p in self.inhalt if self.eingehend[p] == 0]
        self.assertEqual(verwaist, [], f"ohne eingehenden Verweis: {verwaist}")

    def test_jede_seite_ist_von_der_startseite_aus_erreichbar(self):
        unerreichbar = [p for p in self.inhalt if p not in self.tiefe]
        self.assertEqual(unerreichbar, [], f"von {START} aus nicht erreichbar: {unerreichbar}")

    def test_keine_seite_liegt_tiefer_als_drei_klicks(self):
        zu_tief = {p: self.tiefe[p] for p in self.inhalt
                   if self.tiefe.get(p, 99) > MAX_TIEFE}
        self.assertEqual(zu_tief, {}, f"tiefer als {MAX_TIEFE} Klicks: {zu_tief}")

    def test_die_sucheingaenge_liegen_einen_klick_entfernt(self):
        """Preisseite und Rechner sollen aus der Suche gefunden werden. Dafür brauchen sie
        internes Gewicht: Kopfleiste oder Fußzeile, also ein Klick von jeder Seite aus."""
        for seite in SUCHEINGAENGE:
            self.assertIn(seite, self.inhalt, f"{seite} fehlt")
            self.assertEqual(self.tiefe.get(seite), 1,
                             f"{seite} liegt {self.tiefe.get(seite)} Klicks tief")
            self.assertGreater(self.eingehend[seite], 30,
                               f"{seite} hat nur {self.eingehend[seite]} eingehende Verweise — "
                               f"steht es noch in der Fußzeile?")

    def test_es_wurde_wirklich_gemessen(self):
        """Ein leerer Seitenbestand wäre bei allen Prüfungen oben grün."""
        self.assertGreater(len(self.inhalt), 40)
        self.assertGreater(sum(self.eingehend.values()), 100)


if __name__ == "__main__":
    unittest.main()
