#!/usr/bin/env python3
"""Erzeugt die KI-Handbuchseiten und das Regal darüber.

    python3 tools/pages/ki_handbuecher.py

Quelle ist das Markdown im Nachbarrepo `Instagram` (siehe BAENDE). Es wird gelesen, nicht
kopiert — ins Repo wandern nur das erzeugte HTML und das PDF. Dieselbe Arbeitsteilung wie bei
tools/handbuch-web.py, das seine Quelle in ~/mobai lässt.

Damit lässt sich die Website ohne das Nachbarrepo nicht neu bauen. Das ist beabsichtigt und
kostet nichts: Das erzeugte HTML ist versioniert; neu gebaut wird nur, wenn sich die Quelle
ändert — und wer sie ändert, hat sie da.

Eine Unschärfe der Quelle, die man kennen sollte: Ein Band liegt im Ordner eines
Instagram-Beitrags (`2026-08-10-sechs-begriffe` enthält Band 1). Der Band ist aber keine
Eigenschaft des Beitrags — spätestens bei einer zweiten Auflage ist unklar, welcher Ordner
gilt. Bis die Bände drüben eigene Ordner haben, ist die Zuordnung hier die einzige Stelle,
an der sie geschrieben steht.
"""
import html
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import coworkweb  # noqa: E402
import handbuchtext  # noqa: E402
import shell  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUELLREPO = "../Instagram/Beitraege"

HUB = "digitalisierung-ki.html"

# Zwei Reihen, weil die Quellen zwei verschiedene Dinge sind: das Praxis-Handbuch ist eine
# aufeinander aufbauende Reihe, die Einzeltitel sind es nicht. `quelle=None` heißt: liegt nur
# als PDF vor und bekommt keine Leseseite.
BAENDE = [
    dict(slug="workflows", kurz_minuten=5, reihe="Praxis-Handbuch", zaehler="Band 1",
         titel="KI-Workflows für Lehrkräfte",
         quelle=f"{QUELLREPO}/2026-08-10-sechs-begriffe/handbuch.md",
         pdf="KI-Workflows-fuer-Lehrkraefte.pdf"),
    dict(slug="materialwerkstatt", kurz_minuten=5, reihe="Praxis-Handbuch", zaehler="Band 2",
         titel="Unterrichtsmaterial selbst bauen",
         quelle=f"{QUELLREPO}/2026-08-10-materialwerkstatt/handbuch.md",
         pdf="Unterrichtsmaterial-selbst-bauen.pdf"),
    dict(slug="ablauf", kurz_minuten=3, reihe="Praxis-Handbuch", zaehler="Band 3",
         titel="Vom Prompt zum Ablauf",
         quelle=f"{QUELLREPO}/2026-08-10-promptest-du-noch/handbuch.md",
         pdf="Vom-Prompt-zum-Ablauf.pdf"),
    dict(slug="assistent", kurz_minuten=4, reihe="Einzeltitel", zaehler="Workbook",
         titel="Dein KI-Unterrichtsassistent",
         quelle=f"{QUELLREPO}/2026-08-09-stapel-und-assistent/handbuch.md",
         pdf="Dein-KI-Unterrichtsassistent.pdf"),
    dict(slug="cowork", reihe="Einzeltitel", zaehler="Heft 1",
         titel="Claude Cowork — Erste Orientierung",
         # Einziger Titel mit HTML- statt Markdown-Quelle: Er ist als Druckheft gesetzt worden,
         # nicht geschrieben. tools/coworkweb.py liest ihn und liefert dieselben Felder.
         format="html",
         quelle=(f"{QUELLREPO}/Handbücher Claude Cowork/Einführung Claude/"
                 "handbuch_heft1_quelle.html"),
         pdf_quelle=(f"{QUELLREPO}/Handbücher Claude Cowork/Einführung Claude/"
                     "ClaudeCoworkHeft1.pdf"),
         pdf="Claude-Cowork-Heft-1.pdf"),
]


def lies(b, nur_struktur=False):
    """Ein Band, gleich welcher Quellform — beide Leser liefern dieselben Felder.

    `nur_struktur=True` ist für Aufrufer, die bloß Titel und Kapitelanker brauchen: Beim
    HTML-Heft entfällt damit das Wandeln von 17 Bildern nach WebP.
    """
    pfad = os.path.join(REPO, b["quelle"])
    if b.get("format") == "html":
        return coworkweb.parse(pfad, os.path.join(REPO, "assets", "ki", b["slug"]),
                               f'assets/ki/{b["slug"]}', nur_struktur=nur_struktur)
    return handbuchtext.parse(pfad)


def pdf_quelle(b):
    """Das gebaute PDF liegt neben der Markdown-Quelle in ausgabe/handbuch.pdf."""
    if b.get("pdf_quelle"):
        return os.path.join(REPO, b["pdf_quelle"])
    return os.path.join(REPO, os.path.dirname(b["quelle"]), "ausgabe", "handbuch.pdf")


def mb(pfad):
    return os.path.getsize(pfad) / 1048576


def band_seite(b, m):
    """Eine Leseseite: Kopf, Kapitelspalte und der Textkörper aus der Quelle."""
    nav = "".join(f'<li><a href="#kapitel-{nr}" data-nr="{nr}">{html.escape(t)}</a></li>'
                  for nr, t in m["kapitel"])
    toc = (f'<details class="hbtoc"><summary>Inhalt · {len(m["kapitel"])} Kapitel</summary>'
           f'<div class="answer"><ol>{nav}</ol></div></details>')
    meta = "".join([
        f'<span><b>Stand</b> {html.escape(m["stand"])}</span>',
        f'<span><b>Ausgabe</b> {html.escape(m["ausgabe"])}</span>',
        f'<span><b>Umfang</b> {len(m["kapitel"])} Kapitel</span>',
    ])
    # Das Cowork-Heft hat keine Kurzfassung: Seine Quelle ist gesetztes Druck-HTML und führt
    # die selbstzusammenfassenden Abschnitte nicht, aus denen eine Kurzfassung gebaut wird.
    kurzknopf = (f'<a class="btn b-line" href="ki-kurzfassung-{b["slug"]}.html">'
                 f'Kurzfassung · {b["kurz_minuten"]} Min</a>\n      '
                 if b.get("kurz_minuten") else "")
    body = f'''    <a class="back" href="{HUB}">← Digitalisierung &amp; KI</a>
    <div class="hbhead ki" style="--c:var(--navy)">
      <div>
        <div class="eyebrow">{html.escape(b["reihe"])} · {html.escape(b["zaehler"])}</div>
        <h1>{html.escape(m["titel"])}</h1>
        <p class="claim">{html.escape(m["claim"])}</p>
      </div>
    </div>
    <div class="hbmeta">{meta}</div>
    <div class="cta" style="margin-top:20px">
      {kurzknopf}<a class="btn b-line" href="assets/ki/{b["pdf"]}" download>PDF laden</a>
      <a class="btn b-line" href="ki-glossar.html">Glossar</a>
    </div>
    {toc}

    <div class="hblayout" style="--c:var(--navy)">
      <nav class="hbnav ki" aria-label="Kapitel">
        <h4>Kapitel</h4>
        <ol>{nav}</ol>
      </nav>
      <article class="hb ki">
        {f'<blockquote>{m["merksatz"]}</blockquote>' if m["merksatz"] else ""}
        {m["anreisser"]}
{m["body"]}
        <div class="hbfoot">
          <a href="ki-handbuecher.html">← Alle KI-Handbücher</a>
          <a href="{HUB}">Digitalisierung &amp; KI →</a>
        </div>
      </article>
    </div>
'''
    titel = f'{m["titel"]} — ClassTiles'
    desc = (f'{m["titel"]}: {m["claim"]} {b["reihe"]}, {b["zaehler"]} — '
            f'{len(m["kapitel"])} Kapitel, online lesbar und als PDF. '
            f'Für Lehrkräfte, die KI im Unterricht verlässlich einsetzen wollen.')
    return shell.page(f"ki-handbuch-{b['slug']}.html", titel, desc, body)


def kachel(b):
    # Die Kurzfassung steht vorn und solide: Wer das Regal ansieht, hat sich noch nicht für
    # 7.000 Wörter entschieden.
    kn = []
    if b.get("kurz_minuten"):
        kn.append(f'<a class="btn b-solid" href="ki-kurzfassung-{b["slug"]}.html">Kurzfassung</a>')
    if b["quelle"]:
        stil = "b-line" if kn else "b-solid"
        kn.append(f'<a class="btn {stil}" href="ki-handbuch-{b["slug"]}.html">Online lesen</a>')
    kn.append(f'<a class="btn b-line" href="assets/ki/{b["pdf"]}" download>'
              f'PDF · {mb(os.path.join(REPO, "assets", "ki", b["pdf"])):.1f} MB</a>')
    fakten = b["fakten"] if b["quelle"] else "Nur als PDF"
    return (f'<div class="mod" style="--c:var(--navy-soft)">'
            f'<b>{html.escape(b["titel"])}</b>'
            f'<span>{html.escape(b["claim"])}</span>'
            f'<span class="hbfacts">{html.escape(fakten)}</span>'
            f'<div class="hblinks">{"".join(kn)}</div></div>')


def regal():
    reihen = []
    for name, text in (("Praxis-Handbuch",
                        "Drei Bände, die aufeinander aufbauen. Band 1 klärt die Begriffe und "
                        "die Methode, Band 2 wendet sie auf Unterrichtsmaterial an, Band 3 "
                        "zeigt, wohin der lange Prompt verschwindet."),
                       ("Einzeltitel",
                        "Steht für sich und setzt keinen Band voraus.")):
        kacheln = "".join(kachel(b) for b in BAENDE if b["reihe"] == name)
        reihen.append(f'''    <section class="rev">
      <div class="head"><h2>{name}</h2><p>{text}</p></div>
      <div class="grid">{kacheln}</div>
    </section>''')

    body = f'''    <a class="back" href="{HUB}">← Digitalisierung &amp; KI</a>
    <div class="pagetitle" style="max-width:none">
      <div class="eyebrow">KI-Handbücher</div>
      <h1>Wie KI im Schulalltag verlässlich wird</h1>
      <p class="mlead">Keine Prompt-Sammlung. Die Bände zeigen, wie aus einem einmal
      erklärten Ablauf ein Ergebnis wird, auf das du dich verlassen kannst, und sie sagen
      an jedem Kapitelende, wo die Methode aufhört. Online lesen oder als PDF mitnehmen.</p>
    </div>

{chr(10).join(reihen)}

    <section class="rev">
      <p class="note">Schülerdaten gehören in keinen dieser Abläufe. Jeder Band sagt an der
      Stelle, an der es darauf ankommt, welche Angaben draußen bleiben, und
      <a href="ki-material.html">die Blätter für die Klasse</a> setzen dieselbe Linie für
      deine Schülerinnen und Schüler.</p>
    </section>
'''
    desc = ("KI-Handbücher für Lehrkräfte: verlässliche, wiederholbare Abläufe statt "
            "Prompt-Sammlungen: Unterrichtsmaterial, Datenschutz und Grenzen. Online "
            "lesbar und als PDF.")
    return shell.page("ki-handbuecher.html", "KI-Handbücher — ClassTiles", desc, body)


def main():
    os.makedirs(os.path.join(REPO, "assets", "ki"), exist_ok=True)
    for b in BAENDE:
        quelle = pdf_quelle(b)
        if not os.path.exists(quelle):
            sys.exit(f"PDF fehlt: {quelle}")
        shutil.copyfile(quelle, os.path.join(REPO, "assets", "ki", b["pdf"]))

        if not b["quelle"]:
            b.setdefault("claim", "")
            continue
        m = lies(b)
        b["claim"] = m["claim"]
        umfang = f'{len(m["kapitel"])} Kapitel'
        if m.get("bilder"):
            umfang += f' · {m["bilder"]} Abbildungen'
        b["fakten"] = f'{umfang} · {m["ausgabe"]} · Stand {m["stand"]}'
        with open(os.path.join(REPO, f"ki-handbuch-{b['slug']}.html"), "w",
                  encoding="utf-8") as f:
            f.write(band_seite(b, m))
        print(f'  ki-handbuch-{b["slug"]}.html — {len(m["kapitel"])} Kapitel, '
              f'{len(m["abschnitte"])} Abschnitte')

    with open(os.path.join(REPO, "ki-handbuecher.html"), "w", encoding="utf-8") as f:
        f.write(regal())
    lesbar = sum(1 for b in BAENDE if b["quelle"])
    print(f"  ki-handbuecher.html — {lesbar} von {len(BAENDE)} Titeln online lesbar")


if __name__ == "__main__":
    main()
