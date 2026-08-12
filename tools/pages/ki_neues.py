#!/usr/bin/env python3
"""Erzeugt ki-neues.html aus den Einträgen unter inhalt/neues/.

    python3 tools/pages/ki_neues.py

Ein Eintrag ist eine Datei `JJJJ-MM-TT-kennung.md` mit Kopf und Text:

    ---
    titel: Die KI-Handbücher sind online
    art: Neu                       # Neu · Tipp · Entwicklung
    weiter:
      - Zu den Handbüchern | ki-handbuecher.html
    ---
    Markdown wie in den Handbüchern.

Das Datum steht im Dateinamen und nicht im Kopf: So ist die Sortierung schon im Verzeichnis
sichtbar, und zwei Angaben können nicht auseinanderlaufen.

Alle Einträge stehen auf **einer** Seite. Ein Wochen-Snippet trägt keine eigene URL — 52
Einträge im Jahr sind wenige Kilobyte. Verlinkbar ist trotzdem jeder einzeln: Er trägt seinen
Dateinamen als Anker, und genau der gehört dann in die Instagram-Bio.
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import handbuchtext  # noqa: E402
import shell  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUELLE = os.path.join(REPO, "inhalt", "neues")
HUB = "digitalisierung-ki.html"

ARTEN = ("Neu", "Tipp", "Entwicklung")

MONATE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
          "September", "Oktober", "November", "Dezember")

DATEINAME = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-([a-z0-9-]+)\.md$")


def lies(name):
    treffer = DATEINAME.match(name)
    if not treffer:
        sys.exit(f"neues/{name}: Dateiname muss JJJJ-MM-TT-kennung.md sein")
    jahr, monat, tag, kennung = treffer.groups()

    with open(os.path.join(QUELLE, name), encoding="utf-8") as f:
        zeilen = f.read().split("\n")
    if zeilen[0].strip() != "---" or "---" not in zeilen[1:]:
        sys.exit(f"neues/{name}: kein Kopf zwischen zwei ---")
    ende = zeilen.index("---", 1)

    kopf, weiter, in_weiter = {}, [], False
    for z in zeilen[1:ende]:
        if in_weiter and z.strip().startswith("- "):
            beschriftung, _, ziel = z.strip()[2:].partition("|")
            if not ziel.strip():
                sys.exit(f"neues/{name}: „weiter“ braucht „Beschriftung | ziel.html“")
            weiter.append((beschriftung.strip(), ziel.strip()))
            continue
        in_weiter = z.strip() == "weiter:"
        if not in_weiter and ":" in z:
            k, v = z.split(":", 1)
            kopf[k.strip()] = v.strip()

    for pflicht in ("titel", "art"):
        if not kopf.get(pflicht):
            sys.exit(f"neues/{name}: „{pflicht}“ fehlt im Kopf")
    if kopf["art"] not in ARTEN:
        sys.exit(f'neues/{name}: art „{kopf["art"]}“ unbekannt — erlaubt: {", ".join(ARTEN)}')
    for _, ziel in weiter:
        datei = ziel.split("#")[0]
        if datei and not os.path.exists(os.path.join(REPO, datei)):
            sys.exit(f"neues/{name}: Ziel {datei} gibt es nicht")

    return dict(sortier=(jahr, monat, tag), jahr=jahr, kennung=f"{jahr}-{monat}-{tag}-{kennung}",
                datum=f"{int(tag)}. {MONATE[int(monat) - 1]} {jahr}",
                titel=kopf["titel"], art=kopf["art"], weiter=weiter,
                text=handbuchtext.fliesstext("\n".join(zeilen[ende + 1:])))


def eintrag(e):
    weiter = "".join(f'<a href="{z}">{html.escape(b)} →</a>' for b, z in e["weiter"])
    return (f'<article class="neu" id="{e["kennung"]}">'
            f'<div class="neukopf"><time>{e["datum"]}</time>'
            f'<span class="art art-{e["art"].lower()}">{e["art"]}</span></div>'
            f'<h3><a href="#{e["kennung"]}">{html.escape(e["titel"])}</a></h3>'
            f'{e["text"]}'
            + (f'<div class="neuweiter">{weiter}</div>' if weiter else "")
            + "</article>")


def seite(eintraege):
    bloecke, jahre = [], []
    for e in eintraege:
        if e["jahr"] not in jahre:
            jahre.append(e["jahr"])
            if len(jahre) > 1:
                bloecke.append(f'<h2 class="neujahr">{e["jahr"]}</h2>')
        bloecke.append(eintrag(e))

    body = f'''    <a class="back" href="{HUB}">← Digitalisierung &amp; KI</a>
    <div class="pagetitle" style="max-width:none">
      <div class="eyebrow">Neues</div>
      <h1>Was sich getan hat</h1>
      <p class="mlead">Kurze Notizen zu Entwicklungen rund um KI in der Schule und Handgriffe,
      die sich im Unterricht bewährt haben. Kein Newsletter, keine Anmeldung. Die Seite
      steht hier, und wer mag, schaut vorbei.</p>
    </div>

    <section class="neues">
{chr(10).join("      " + b for b in bloecke)}
    </section>

    <section class="rev">
      <p class="note">Die ausführlichen Fassungen stehen in den
      <a href="ki-handbuecher.html">Handbüchern</a>; angekündigt wird hier Erscheinendes auch
      <a href="https://www.instagram.com/classtiles/" target="_blank" rel="noopener noreferrer">auf
      Instagram</a>.</p>
    </section>
'''
    desc = ("Neues zu KI und Digitalisierung in der Schule: kurze Notizen zu Entwicklungen "
            "und erprobte Handgriffe für den Unterricht.")
    return shell.page("ki-neues.html", "Neues — ClassTiles", desc, body)


def main():
    if not os.path.isdir(QUELLE):
        sys.exit(f"Verzeichnis fehlt: {os.path.relpath(QUELLE, REPO)}")
    namen = sorted(n for n in os.listdir(QUELLE) if n.endswith(".md"))
    if not namen:
        sys.exit("Keine Einträge unter inhalt/neues/")
    eintraege = sorted((lies(n) for n in namen), key=lambda e: e["sortier"], reverse=True)
    with open(os.path.join(REPO, "ki-neues.html"), "w", encoding="utf-8") as f:
        f.write(seite(eintraege))
    print(f'  ki-neues.html — {len(eintraege)} Einträge, neuester {eintraege[0]["datum"]}')


if __name__ == "__main__":
    main()
