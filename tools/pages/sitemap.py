#!/usr/bin/env python3
"""Erzeugt sitemap.xml — das Inhaltsverzeichnis der Website für Suchmaschinen.

    python3 tools/pages/sitemap.py
    python3 tools/pages/sitemap.py --check   # ändert nichts, Exit-Code 1 bei Abweichung

Ohne Sitemap muss Google jede Seite über Verweise finden. Bei einer Website ohne nennenswerte
eingehende Links dauert das lange und bleibt lückenhaft — der KI-Bereich etwa liegt zwei Klicks
von der Startseite entfernt.

`lastmod` kommt aus dem Git-Verlauf der jeweiligen Datei, nicht aus dem Dateidatum: ein Auschecken
setzt Dateidaten neu, und eine Sitemap, die jeder Seite von gestern behauptet, verliert ihren Wert.
Seiten, die noch nicht eingecheckt sind, bekommen kein `lastmod` — lieber keine Angabe als eine
erfundene.

`priority` und `changefreq` fehlen mit Absicht: Google wertet beides seit Jahren nicht aus.
"""
import argparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import shell  # noqa: E402

ZIEL = os.path.join(REPO, "sitemap.xml")
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML = "http://www.w3.org/1999/xhtml"


def seiten():
    out = [n for n in sorted(os.listdir(REPO)) if n.endswith(".html")]
    endir = os.path.join(REPO, "en")
    out += ["en/" + n for n in sorted(os.listdir(endir)) if n.endswith(".html")]
    return out


def zuletzt_geaendert(path):
    """Datum des letzten Commits, der diese Datei angefasst hat (JJJJ-MM-TT), oder None."""
    r = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%cs", "--", path],
                       capture_output=True, text=True)
    return r.stdout.strip() or None


def baum():
    ET.register_namespace("", NS)
    ET.register_namespace("xhtml", XHTML)
    wurzel = ET.Element(f"{{{NS}}}urlset")

    for path in seiten():
        eintrag = ET.SubElement(wurzel, f"{{{NS}}}url")
        ET.SubElement(eintrag, f"{{{NS}}}loc").text = shell.canonical_of(path)
        stand = zuletzt_geaendert(path)
        if stand:
            ET.SubElement(eintrag, f"{{{NS}}}lastmod").text = stand
        # Die Sprachgruppe steht zusätzlich hier — dieselbe Aussage wie die hreflang-Verweise im
        # Seitenkopf. Google liest beides und bestätigt das eine mit dem anderen.
        if shell.is_paired(path):
            twin = shell.twin_page(path)
            de, en = (path, twin) if shell.lang_of(path) == "de" else (twin, path)
            for code, ziel in (("de", de), ("en", en), ("x-default", de)):
                ET.SubElement(eintrag, f"{{{XHTML}}}link",
                              rel="alternate", hreflang=code, href=shell.canonical_of(ziel))

    ET.indent(wurzel, space="  ")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            + ET.tostring(wurzel, encoding="unicode") + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    neu = baum()
    alt = open(ZIEL, encoding="utf-8").read() if os.path.exists(ZIEL) else None

    if a.check:
        if neu != alt:
            sys.exit("sitemap.xml ist nicht auf dem Stand — python3 tools/pages/sitemap.py")
        print(f"sitemap.xml aktuell ({len(seiten())} Seiten)")
        return

    open(ZIEL, "w", encoding="utf-8").write(neu)
    print(f"sitemap.xml geschrieben — {len(seiten())} Seiten"
          + ("" if neu != alt else " (unverändert)"))


if __name__ == "__main__":
    main()
