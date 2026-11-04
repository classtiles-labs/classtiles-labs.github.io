#!/usr/bin/env python3
"""Erzeugt den KI-Kurs: ki-kurs.html (Übersicht) und ki-kurs-<id>.html je gebauter Station.

    python3 tools/pages/ki_kurs.py           Seiten schreiben (veraltete Stationsseiten löschen)
    python3 tools/pages/ki_kurs.py --check   nur vergleichen, Exit-Code 1 bei Abweichung

Quelle ist das Register inhalt/kurs/netz.json: Linien und Stationen in Fahrtrichtung. Eine
Station mit "status": "gebaut" braucht ein Inhaltsfragment inhalt/kurs/stationen/<id>.html und
eine Beschreibung (≤ 160 Zeichen); geplante Stationen erscheinen nur im Netz, „in Planung“.

Den Rahmen jeder Seite schreibt dieser Generator, den Inhalt das Fragment. Das Verhalten (Netz
zeichnen, Fortschritt, Erlebnisse) kommt aus assets/kurs/kurs.js; ohne JavaScript bleiben alle
gebauten Stationen als Links und alle Tickets als Text lesbar.

Danach immer: python3 tools/apply-shell.py && python3 tools/pages/sitemap.py
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shell  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NETZ = os.path.join(REPO, "inhalt", "kurs", "netz.json")
HUB = "digitalisierung-ki.html"
UEBERSICHT = "ki-kurs.html"

SLOGAN = "Die KI-Welt läuft rasant. Keine Sorge: Wir helfen dir, den Anschluss zu behalten."
LINIEN = ("E", "A", "B")
TICKET = re.compile(r'class="ticket-prompt"')
STATIONSSEITE = re.compile(r"^ki-kurs-[a-z0-9-]+\.html$")
KENNUNG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def dateiname(sid):
    return f"ki-kurs-{sid}.html"


def lade_netz(pfad=NETZ):
    """Register lesen und prüfen; bei gebauten Stationen das Fragment anhängen."""
    name = os.path.relpath(pfad, REPO)
    with open(pfad, encoding="utf-8") as f:
        netz = json.load(f)
    if netz.get("version") != 1:
        sys.exit(f"{name}: version muss 1 sein")
    if [l["id"] for l in netz.get("linien", [])] != list(LINIEN):
        sys.exit(f"{name}: linien müssen genau E, A, B in dieser Reihenfolge sein")
    stationen = netz.get("stationen", [])
    ids = [s.get("id") for s in stationen]
    for sid in ids:
        if not sid or not KENNUNG.match(sid):
            sys.exit(f"{name}: ungültige Kennung {sid!r}")
        if ids.count(sid) > 1:
            sys.exit(f"{name}: Kennung {sid} doppelt")
    quelle = os.path.join(os.path.dirname(pfad), "stationen")
    for s in stationen:
        sid = s["id"]
        if s.get("linie") not in LINIEN:
            sys.exit(f"{name}: {sid} hat unbekannte Linie {s.get('linie')!r}")
        if not s.get("titel"):
            sys.exit(f"{name}: {sid} ohne Titel")
        if s.get("status") not in ("gebaut", "geplant"):
            sys.exit(f"{name}: {sid} hat unbekannten status {s.get('status')!r}")
        if s.get("umstieg") and s["umstieg"] not in ids:
            sys.exit(f"{name}: {sid} steigt um nach {s['umstieg']}, die Station gibt es nicht")
        if s.get("umstieg") == sid:
            sys.exit(f"{name}: {sid} steigt in sich selbst um")
        if s["status"] != "gebaut":
            continue
        besch = s.get("beschreibung", "").strip()
        if not besch:
            sys.exit(f"{name}: {sid} ist gebaut, aber ohne beschreibung")
        if len(besch) > 160:
            sys.exit(f"{name}: beschreibung von {sid} hat {len(besch)} Zeichen (höchstens 160)")
        frag = os.path.join(quelle, f"{sid}.html")
        if not os.path.exists(frag):
            sys.exit(f"{name}: {sid} ist gebaut, aber {os.path.relpath(frag, REPO)} fehlt")
        with open(frag, encoding="utf-8") as f:
            text = f.read()
        tickets = len(TICKET.findall(text))
        if tickets != 1:
            sys.exit(f"{os.path.relpath(frag, REPO)}: braucht genau ein class=\"ticket-prompt\", "
                     f"gefunden {tickets}")
        s["fragment"] = text.rstrip("\n")
    return netz


def _linie(netz, lid):
    return next(l for l in netz["linien"] if l["id"] == lid)


def _auf_linie(netz, lid):
    return [s for s in netz["stationen"] if s["linie"] == lid]


def _station(netz, sid):
    return next(s for s in netz["stationen"] if s["id"] == sid)


def _badge(lid):
    return f'<span class="linie-badge linie-{lid.lower()}">{lid}</span>'


def _netz_json(netz):
    ohne = {**netz, "stationen": [{k: v for k, v in s.items() if k != "fragment"}
                                  for s in netz["stationen"]]}
    # „</" schlösse den Skriptblock vorzeitig; im JSON ist „<\/" gleichwertig.
    return json.dumps(ohne, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def _fuss(netz):
    return (f'  <script type="application/json" id="kurs-netz">{_netz_json(netz)}</script>\n'
            f'  <script type="module" src="assets/kurs/kurs.js"></script>')


def _umstieg_html(netz, s):
    if not s.get("umstieg"):
        return ""
    ziel = _station(netz, s["umstieg"])
    linie = _linie(netz, ziel["linie"])
    titel = html.escape(ziel["titel"])
    if ziel["status"] == "gebaut":
        hin = f'<a href="{dateiname(ziel["id"])}">{titel}</a>'
    else:
        hin = f'{titel} <span class="kurs-geplant">in Planung</span>'
    return (f'<p class="kurs-umstieg">Umsteigen: {_badge(linie["id"])} '
            f'{html.escape(linie["name"])} ab {hin}</p>')


def _einstiege(netz):
    """Ersatz für die Fahrkarte ohne JavaScript: Einstieg in jede Linie, die schon fährt."""
    links = []
    for lid in LINIEN:
        erste = next((s for s in _auf_linie(netz, lid) if s["status"] == "gebaut"), None)
        if erste:
            linie = _linie(netz, lid)
            links.append(f'<a href="{dateiname(erste["id"])}">{_badge(lid)} '
                         f'{html.escape(linie["name"])}</a>')
    if not links:
        return ""
    return f'<p class="fk-einstiege">Direkt einsteigen: {" · ".join(links)}</p>'


def uebersicht(netz):
    listen = []
    for lid in LINIEN:
        linie = _linie(netz, lid)
        eintraege = []
        for s in _auf_linie(netz, lid):
            titel = html.escape(s["titel"])
            if s["status"] == "gebaut":
                inhalt = f'<a href="{dateiname(s["id"])}">{titel}</a>'
                klasse = ""
            else:
                inhalt = f'{titel} <span class="kurs-geplant">in Planung</span>'
                klasse = ' class="geplant"'
            if s.get("umstieg"):
                ziel = _station(netz, s["umstieg"])
                inhalt += (f' <span class="kurs-umstieg-hinweis">Umstieg zu '
                           f'{_badge(ziel["linie"])}</span>')
            eintraege.append(f'          <li data-station="{s["id"]}"{klasse}>{inhalt}</li>')
        kurz = f'<p>{html.escape(linie["kurz"])}</p>' if linie.get("kurz") else ""
        listen.append(f'''      <div class="kurs-linie" data-linie="{lid}">
        <h3>{_badge(lid)} {html.escape(linie["name"])}</h3>
        {kurz}
        <ol class="kurs-liste" data-linie="{lid}">
{chr(10).join(eintraege)}
        </ol>
      </div>''')

    body = f'''    <a class="back" href="{HUB}">← Digitalisierung &amp; KI</a>
    <link rel="stylesheet" href="assets/kurs/kurs.css">
    <div class="pagetitle kurs-kopf" style="max-width:none">
      <div class="eyebrow">KI-Kurs für Lehrkräfte</div>
      <h1>{SLOGAN}</h1>
      <p class="mlead">Drei Linien, kurze Stationen. Jede Station hat etwas zum Ausprobieren und
      einen Prompt zum Mitnehmen. Ohne Anmeldung.</p>
    </div>

    <section id="fahrkarte" class="kurs-fahrkarte">
      <div data-erlebnis="fahrkarte">
        <h2>Fahrkarte lösen</h2>
        <p>3 Fragen, 1 Minute: Danach weißt du, auf welcher Linie du einsteigst. Du kannst
        auch direkt unten im Liniennetz einsteigen.</p>
        {_einstiege(netz)}
      </div>
    </section>

    <section class="kurs-netz">
      <h2>Das Liniennetz</h2>
      <div id="liniennetz" hidden></div>
      <div class="kurs-listen">
{chr(10).join(listen)}
      </div>
    </section>

    <section id="fahrplan" class="kurs-fahrplan">
      <h2>Fahrplanänderungen</h2>
      <p>Hier steht, was sich in der KI-Welt geändert hat und was es für den Unterricht heißt.
      Alle Notizen stehen unter <a href="ki-neues.html">Neues</a>.</p>
    </section>

    <div id="kurs-fortschritt"></div>
{_fuss(netz)}
'''
    desc = ("Interaktiver KI-Kurs für Lehrkräfte: Grundlagen, Alltag und eigene Werkzeuge. "
            "Kurze Stationen zum Ausprobieren, mit Prompts zum Mitnehmen. Ohne Anmeldung.")
    return shell.page(UEBERSICHT, "KI-Kurs — ClassTiles", desc, body)


def station(netz, s):
    linie = _linie(netz, s["linie"])
    alle = _auf_linie(netz, s["linie"])
    nr = alle.index(s) + 1
    gebaut = [x for x in alle if x["status"] == "gebaut"]
    i = gebaut.index(s)
    nav = []
    if i > 0:
        v = gebaut[i - 1]
        nav.append(f'<a rel="prev" href="{dateiname(v["id"])}">← {html.escape(v["titel"])}</a>')
    if i < len(gebaut) - 1:
        n = gebaut[i + 1]
        nav.append(f'<a rel="next" href="{dateiname(n["id"])}">Weiter: '
                   f'{html.escape(n["titel"])} →</a>')
    nav.append(f'<a class="kurs-zum-netz" href="{UEBERSICHT}">Zum Liniennetz</a>')
    umstieg = _umstieg_html(netz, s)
    body = f'''    <a class="back" href="{UEBERSICHT}">← KI-Kurs: Liniennetz</a>
    <link rel="stylesheet" href="assets/kurs/kurs.css">
    <main class="station" data-station="{s["id"]}" data-linie="{s["linie"]}">
      <header class="station-kopf">
        <div class="eyebrow">{_badge(s["linie"])} {html.escape(linie["name"])} · Station {nr} von {len(alle)}</div>
        <h1>{html.escape(s["titel"])}</h1>
      </header>
{s["fragment"]}
      <nav class="station-nav">
        {umstieg}
        {" ".join(nav)}
      </nav>
      <div id="kurs-fortschritt"></div>
    </main>
{_fuss(netz)}
'''
    return shell.page(dateiname(s["id"]), f'{s["titel"]} · KI-Kurs — ClassTiles',
                      s["beschreibung"], body)


def seiten(netz):
    out = {UEBERSICHT: uebersicht(netz)}
    for s in netz["stationen"]:
        if s["status"] == "gebaut":
            out[dateiname(s["id"])] = station(netz, s)
    return out


def main(argv):
    check = "--check" in argv
    soll = seiten(lade_netz())
    vorhanden = {n for n in os.listdir(REPO) if STATIONSSEITE.match(n)}
    abweichung = []
    for name, text in soll.items():
        ziel = os.path.join(REPO, name)
        ist = open(ziel, encoding="utf-8").read() if os.path.exists(ziel) else None
        if ist != text:
            abweichung.append(name)
            if not check:
                with open(ziel, "w", encoding="utf-8") as f:
                    f.write(text)
    for name in sorted(vorhanden - set(soll)):
        abweichung.append(f"{name} (veraltet)")
        if not check:
            os.remove(os.path.join(REPO, name))
    if check:
        if abweichung:
            print("Nicht auf dem Stand: " + ", ".join(abweichung))
            return 1
        return 0
    print(f"  KI-Kurs — {len(soll)} Seiten" + (f", geändert: {', '.join(abweichung)}" if abweichung else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
