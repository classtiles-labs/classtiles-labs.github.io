#!/usr/bin/env python3
"""Erzeugt handbuecher.html — die Übersicht über die sechs Modulhandbücher.

    python3 tools/pages/handbuecher.py

Die Umfangszahlen stehen in HANDBUECHER und werden beim Erzeugen eines Handbuchs von
tools/handbuch-web.py ausgegeben. Kommt ein Handbuch dazu, hier den Eintrag ergänzen.

Die Seite wird erzeugt und nicht von Hand gepflegt: sechs sehr ähnliche Kacheln, von denen
vier nach und nach durch fertige ersetzt werden.
"""
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shell  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Reihenfolge und Farben folgen den Modulkacheln der Startseite — Handbuch und Modulseite
# sollen sichtbar zusammengehören. Ein Eintrag ohne `claim` gilt als noch nicht geschrieben.
HANDBUECHER = [
    dict(modul=1, farbe="m1", ikone="grades", titel="Notenverwaltung",
         claim="Noten erfassen und auswerten",
         seite="handbuch-notenverwaltung.html",
         pdf="assets/handbuch/ClassTiles-Handbuch-Notenverwaltung.pdf",
         kapitel=12, abbildungen=48, stand="7. August 2026", app="1.0.6"),
    dict(modul=2, farbe="m2", ikone="calendar", titel="Kalender", claim=None),
    dict(modul=3, farbe="m3", ikone="planning", titel="Planung", claim=None),
    dict(modul=4, farbe="m4", ikone="groups", titel="Gruppen & Sitzordnung",
         claim="Gruppen bilden und Plätze zuweisen",
         seite="handbuch-gruppen-sitzordnung.html",
         pdf="assets/handbuch/ClassTiles-Handbuch-Gruppen-Sitzordnung.pdf",
         kapitel=10, abbildungen=28, stand="8. August 2026", app="1.0.6"),
    dict(modul=5, farbe="m5", ikone="documentation", titel="Dokumentation", claim=None),
    dict(modul=6, farbe="m6", ikone="tasks", titel="Klassengeschäfte", claim=None),
]


def mb(rel):
    return os.path.getsize(os.path.join(REPO, rel)) / 1048576


def kachel(h):
    kopf = (f'<span class="glyph">{shell.GLYPHS[h["ikone"]]}</span>'
            f'<b>{html.escape(h["titel"])}</b>')
    if not h["claim"]:
        return (f'<div class="mod soon-tile" style="--c:var(--{h["farbe"]})">{kopf}'
                f'<span>Modul {h["modul"]} von 6</span>'
                f'<em>In Vorbereitung</em></div>')
    return (f'<div class="mod" style="--c:var(--{h["farbe"]})">{kopf}'
            f'<span>{html.escape(h["claim"])}</span>'
            f'<span class="hbfacts">{h["kapitel"]} Kapitel · {h["abbildungen"]} Abbildungen · '
            f'Stand {html.escape(h["stand"])} · App {h["app"]}</span>'
            f'<div class="hblinks"><a class="btn b-solid" href="{h["seite"]}">Online lesen</a>'
            f'<a class="btn b-line" href="{h["pdf"]}" download>PDF · {mb(h["pdf"]):.0f} MB</a></div>'
            f'</div>')


BODY = '''    <div class="pagetitle" style="max-width:none">
      <div class="eyebrow">Handbücher</div>
      <h1>Ein Handbuch je Modul</h1>
      <p class="mlead">Schritt für Schritt durch ClassTiles — mit Bildern aus der echten App,
      einer echten Beispielklasse und zu jeder Abbildung zwei Sätzen: was Sie sehen und was Sie
      hier tun können. Online lesen oder als PDF mitnehmen.</p>
    </div>

    <section style="padding:34px 0 0">
      <div class="grid">{kacheln}</div>
      <p class="note">Die Handbücher entstehen nacheinander. Zwei sind fertig, die übrigen folgen —
      wer wissen will, wann, findet die Ankündigungen
      <a href="https://www.instagram.com/classtiles/" target="_blank" rel="noopener noreferrer">auf
      Instagram</a>.</p>
    </section>
'''


def main():
    body = BODY.replace("{kacheln}", "".join(kachel(h) for h in HANDBUECHER))
    fertig = [h for h in HANDBUECHER if h["claim"]]
    desc = (f"Benutzerhandbücher zur Lehrer-App ClassTiles: "
            f"{', '.join(h['titel'] for h in fertig)} — online lesbar und als PDF. "
            f"Ein Handbuch je Modul, weitere in Vorbereitung.")
    page = shell.page("handbuecher.html", "Handbücher — ClassTiles", desc, body)
    with open(os.path.join(REPO, "handbuecher.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print(f"handbuecher.html — {len(fertig)} von {len(HANDBUECHER)} Handbüchern verfügbar")


if __name__ == "__main__":
    main()
