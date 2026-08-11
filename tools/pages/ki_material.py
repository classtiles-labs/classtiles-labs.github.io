#!/usr/bin/env python3
"""Erzeugt ki-material.html — die drei Blätter für die Klasse.

    python3 tools/pages/ki_material.py

Titel, Untertitel und Einsatzort stehen im Kopf der Markdown-Quellen und werden von dort
gelesen statt hier abgeschrieben: Auf dem ausgedruckten Blatt und auf der Website soll
dasselbe stehen, auch nach der nächsten Überarbeitung.
"""
import html
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shell  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUELLE = "../Instagram/Beitraege/Material"

HUB = "digitalisierung-ki.html"

# Reihenfolge = Reihenfolge des Einsatzes: erst aushängen, dann austeilen, dann abgeben lassen.
# `wann` ist der einzige Text, der hier und nicht in der Quelle steht — er beantwortet eine
# Frage, die sich auf dem Blatt selbst nicht stellt.
BLAETTER = [
    dict(name="ki-ampel", pdf="KI-Ampel.pdf",
         wann="Einmal ausdrucken und aufhängen. Die Ampel klärt den Normalfall, damit nicht "
              "jede Aufgabe neu verhandelt wird."),
    dict(name="ki-handreichung", pdf="KI-Handreichung.pdf",
         wann="Zu Beginn der Reihe einmal austeilen und durchsprechen. Erklärt, warum es die "
              "Regeln gibt — die Ampel sagt nur, wie sie lauten."),
    dict(name="ki-protokoll", pdf="KI-Protokoll.pdf",
         wann="Liegt jeder Abgabe bei. Wer offenlegt, wie ein Ergebnis entstanden ist, muss "
              "sich hinterher nicht rechtfertigen."),
]


def kopf(pfad):
    """Liest den YAML-Kopf eines Blattes — nur die Felder, die diese Seite braucht."""
    with open(pfad, encoding="utf-8") as f:
        zeilen = f.read().split("\n")
    if zeilen[0].strip() != "---":
        sys.exit(f"{pfad}: kein Kopf")
    ende = zeilen.index("---", 1)
    feld, aus = None, {}
    for z in zeilen[1:ende]:
        if z.startswith(" ") and feld:                       # Fortsetzung eines „key: |"-Blocks
            aus[feld] = (aus[feld] + " " + z.strip()).strip()
        elif ":" in z:
            feld, wert = z.split(":", 1)
            feld = feld.strip()
            aus[feld] = "" if wert.strip() == "|" else wert.strip()
    return aus


def kachel(b):
    k = b["kopf"]
    return (f'<div class="mod" style="--c:var(--navy-soft)">'
            f'<b>{html.escape(k["titel"])}</b>'
            f'<span>{html.escape(k["untertitel"])}</span>'
            f'<span class="hbfacts">{html.escape(k["fusszeile"])} · Stand '
            f'{html.escape(k["stand"])}</span>'
            f'<p class="mlead" style="font-size:.95rem">{html.escape(b["wann"])}</p>'
            f'<div class="hblinks"><a class="btn b-solid" href="assets/ki/{b["pdf"]}" download>'
            f'PDF laden · A4</a></div></div>')


def seite():
    kacheln = "".join(kachel(b) for b in BLAETTER)
    body = f'''    <a class="back" href="{HUB}">← Digitalisierung &amp; KI</a>
    <div class="pagetitle" style="max-width:none">
      <div class="eyebrow">Material für die Klasse</div>
      <h1>Drei Blätter, und die Sache ist geregelt</h1>
      <p class="mlead">KI-Nutzung lässt sich nicht verbieten und nicht ignorieren — aber sie
      lässt sich regeln, und zwar kürzer, als man denkt. Ein Aushang, ein Merkblatt, ein
      Protokoll: fertig gesetzt auf A4, zum Ausdrucken und Weitergeben.</p>
    </div>

    <section style="padding:34px 0 0">
      <div class="grid">{kacheln}</div>
    </section>

    <section class="rev">
      <div class="box">
        <h2>Warum drei und nicht eins</h2>
        <p>Die drei Blätter beantworten drei verschiedene Fragen, und ein einziges Blatt
        beantwortet keine davon gut. <b>Was gilt?</b> steht an der Wand, damit es niemand
        suchen muss. <b>Warum gilt das?</b> braucht Platz und ein Gespräch, sonst wird die
        Regel nur befolgt und nicht verstanden. <b>Was habe ich getan?</b> gehört an die
        Arbeit, nicht an die Wand.</p>
        <p>Die Blätter sind so geschrieben, dass sie ohne Anpassung funktionieren. Wenn an
        deiner Schule etwas anderes gilt, ist die Ampel die Stelle, an der du es änderst —
        Handreichung und Protokoll bleiben davon unberührt.</p>
      </div>
    </section>

    <section class="rev">
      <p class="note">Woher die Linie kommt, steht in den
      <a href="ki-handbuecher.html">KI-Handbüchern</a>: dieselbe Ampel gilt dort für dich als
      Lehrkraft, eine Etage höher — mit Klassenlisten, Diagnosen und Zeugnissen statt
      Hausaufgaben.</p>
    </section>
'''
    desc = ("KI-Regeln für die Klasse: Ampel für den Aushang, Handreichung für die Lerngruppe "
            "und Protokoll für die Abgabe — drei fertige A4-Blätter zum Ausdrucken.")
    return shell.page("ki-material.html", "Material für die Klasse — ClassTiles", desc, body)


def main():
    os.makedirs(os.path.join(REPO, "assets", "ki"), exist_ok=True)
    for b in BLAETTER:
        b["kopf"] = kopf(os.path.join(REPO, QUELLE, b["name"] + ".md"))
        quelle = os.path.join(REPO, QUELLE, "ausgabe", b["name"] + ".pdf")
        if not os.path.exists(quelle):
            sys.exit(f"PDF fehlt: {quelle}")
        shutil.copyfile(quelle, os.path.join(REPO, "assets", "ki", b["pdf"]))
    with open(os.path.join(REPO, "ki-material.html"), "w", encoding="utf-8") as f:
        f.write(seite())
    print(f"  ki-material.html — {len(BLAETTER)} Blätter")


if __name__ == "__main__":
    main()
