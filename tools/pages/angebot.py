#!/usr/bin/env python3
"""Erzeugt digitalisierung-ki.html sowie die beiden englischen Hinweisseiten.

    python3 tools/pages/angebot.py

Die Seite war zuerst nur der Hinweis auf kommende Fortbildungen. Seit es Handbücher und
Material gibt, ist sie der Einstieg in den KI-Bereich — das Angebot ist ein Abschnitt darauf
geblieben. Dass die Datei ihren Namen behält, ist Absicht: Navigationspunkt, englischer
Zwilling und alle bestehenden Links bleiben damit gültig.

Die Türen stehen nach Zeitbedarf, nicht nach Themenlogik. Wer aus einem Reel kommt, hat keine
Frage nach Themen, sondern nach Minuten.

Bewusst ohne Datum und ohne Formular: „In Vorbereitung" verspricht nichts, was reißen kann, und
ein mailto: braucht weder Server noch Auftragsverarbeiter — die Datenschutzerklärung bleibt so,
wie sie ist.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shell  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MAILTO = "mailto:classtiles@icloud.com?subject=Interesse%3A%20Digitalisierung%20%26%20KI"

THEMEN = [
    ("m2", "Unterricht mit KI vorbereiten",
     "Material und Aufgaben erstellen, differenzieren, Rückmeldungen formulieren. Konkret an "
     "eigenen Beispielen — und ebenso ehrlich dort, wo KI mehr Arbeit macht als sie spart."),
    ("m4", "KI, Datenschutz und Recht",
     "Was an der Schule geht und was nicht: DSGVO, EU AI Act, Schülerdaten in KI-Diensten, "
     "Einwilligungen. Ohne Panik, aber mit klaren Linien."),
    ("m1", "Digitaler Lehreralltag",
     "iPad-Workflows, die den Papierstapel wirklich ersetzen: Noten, Planung und Dokumentation "
     "an einer Stelle — unter anderem mit ClassTiles."),
]

FORMATE = [
    ("Fortbildungen und Workshops",
     "Für Kollegien, Fachschaften oder pädagogische Tage — vor Ort oder online. Praxisnah, mit "
     "Zeit zum Ausprobieren am eigenen Gerät statt Folien zum Zusehen."),
    ("Material und Handreichungen",
     "Leitfäden, Vorlagen und erprobte Beispiele zum Mitnehmen. Damit nach der Fortbildung nicht "
     "nur ein gutes Gefühl bleibt, sondern etwas, mit dem sich am Montag arbeiten lässt."),
]


# Die vier Türen des Bereichs, sortiert nach Gewicht: Wer hier ankommt, kam wegen eines Themas,
# und die Handbücher sind die Antwort darauf — sie gehören nicht ans Ende.
#
# Auf den Kacheln stand eine Zeitangabe („2 Minuten"), die den Zeitbedarf des Bereichs meinte.
# Sie ist wieder weg: Neben einem Kacheltext liest sie sich als Lesezeit dieser Kachel, und die
# Türen zu Handbüchern und Glossar führen ohnehin auf Seiten, deren Umfang dort selbst steht.
#
# `ziel=None` heißt: die Seite gibt es noch nicht. Die Kachel steht dann sichtbar als
# „In Vorbereitung" da und verlinkt nichts — ein Link auf eine fehlende Seite wäre kein
# Schönheitsfehler, sondern ein Fehler, den tools/check-links.py meldet.
TUEREN = [
    ("ki-handbuecher.html", "Die Handbücher",
     "Fünf Titel über verlässliche KI-Abläufe — von den sechs Begriffen bis zum "
     "Unterrichtsmaterial, das zu deiner Stunde passt. Zu jedem Band eine Kurzfassung."),
    ("ki-material.html", "Material für die Klasse",
     "KI-Ampel, Handreichung und Protokoll: drei fertige A4-Blätter, mit denen die KI-Nutzung "
     "deiner Lerngruppe geregelt ist."),
    ("ki-glossar.html", "Glossar",
     "Prompt, Kontext, Halluzination, Agent: die Wörter, die überall vorausgesetzt werden — "
     "erklärt, und mit dem Sprung an die Stelle im Handbuch, die ausführlich wird."),
    ("ki-neues.html", "Neu diese Woche",
     "Was sich getan hat, und kleine Handgriffe für den Unterricht — kurz genug für die "
     "Freistunde."),
]


def tuer(ziel, titel, text):
    if not ziel:
        return (f'<div class="mod soon-tile" style="--c:var(--navy-soft)"><b>{titel}</b>'
                f'<span>{text}</span><em>In Vorbereitung</em></div>')
    return (f'<div class="mod" style="--c:var(--navy-soft)"><b>{titel}</b>'
            f'<span>{text}</span>'
            f'<div class="hblinks"><a class="btn b-solid" href="{ziel}">Ansehen</a></div></div>')


def de():
    tueren = "".join(tuer(*t) for t in TUEREN)
    themen = "".join(
        f'<div class="mod" style="--c:var(--{f})"><b>{t}</b><span>{x}</span>'
        f'<em>In Vorbereitung</em></div>' for f, t, x in THEMEN)
    formate = "".join(f'<div class="panel"><h3>{t}</h3><p>{x}</p></div>' for t, x in FORMATE)
    body = f'''    <div class="pagetitle" style="max-width:none">
      <div class="eyebrow">Digitalisierung &amp; KI</div>
      <h1>KI im Unterricht, ohne die Kontrolle abzugeben</h1>
      <p class="mlead">Nicht mehr digital arbeiten, sondern smarter. Hier liegen Handbücher,
      Material für die Klasse und kurze Notizen für Lehrkräfte, die ihren Alltag mit digitalen
      Werkzeugen und KI spürbar entlasten wollen — ohne den Anspruch aufzugeben, zu verstehen,
      was da passiert.</p>
    </div>

    <section style="padding:34px 0 0">
      <div class="two">{tueren}</div>
    </section>

    <section class="rev">
      <div class="box">
        <h2>Woher das kommt</h2>
        <p>ClassTiles ist im eigenen Unterricht entstanden, weil vorhandene Werkzeuge nicht
        gepasst haben. Die Fortbildungen entstehen aus derselben Ecke: aus dem, was sich im
        Schulalltag bewährt hat. <b>Werkzeug statt Selbstzweck</b> — es geht nicht darum, KI
        einzusetzen, sondern darum, Zeit für den Unterricht zurückzugewinnen. Und
        <b>Datenschutz von Anfang an</b>: Schülerdaten gehören nicht versehentlich in einen
        Chatbot.</p>
      </div>
    </section>

    <section class="rev">
      <div class="head">
        <h2>Fortbildungen fürs Kollegium</h2>
        <p>Was hier zum Lesen liegt, gibt es auch als Fortbildung — drei Themen, die in der
        Praxis am häufigsten gefragt werden.</p>
      </div>
      <div class="grid">{themen}</div>
      <div class="two" style="margin-top:26px">{formate}</div>
      <p class="note"><b>Noch gibt es nichts zu buchen.</b> Wenn eines der Themen für dich oder
      dein Kollegium interessant ist, schreib uns — dann melden wir uns, sobald es so weit ist,
      und wissen, woran wirklich Bedarf besteht.</p>
      <div class="cta">
        <a class="btn b-solid" href="{MAILTO}">Interesse anmelden</a>
        <a class="btn b-line" href="ki-handbuecher.html">Zu den KI-Handbüchern</a>
      </div>
    </section>
'''
    desc = ("KI im Unterricht: Handbücher über verlässliche KI-Abläufe, fertiges Material für "
            "die Klasse und Fortbildungen für Kollegien. Von der Lehrkraft hinter ClassTiles.")
    return shell.page("digitalisierung-ki.html", "Digitalisierung & KI — ClassTiles", desc, body)


def en_manuals():
    body = '''    <div class="pagetitle"><h1>Manuals</h1>
      <p>Step-by-step guides to the ClassTiles modules</p></div>
    <main class="prose">
      <p>Each ClassTiles module gets its own manual: every screen explained with a screenshot,
      what you see and what you can do there. Two are finished, the others are being written.</p>
      <p><strong>The manuals are currently available in German only.</strong> They are not
      translated yet, and this page will be updated when that changes.</p>
      <ul>
        <li><a href="../handbuch-notenverwaltung.html">Notenverwaltung</a> (Grades) — 12 chapters,
        48 figures ·
        <a href="../assets/handbuch/ClassTiles-Handbuch-Notenverwaltung.pdf">PDF</a></li>
        <li><a href="../handbuch-gruppen-sitzordnung.html">Gruppen &amp; Sitzordnung</a>
        (Groups &amp; seating) — 10 chapters, 28 figures ·
        <a href="../assets/handbuch/ClassTiles-Handbuch-Gruppen-Sitzordnung.pdf">PDF</a></li>
      </ul>
      <p>In the meantime, every module is described in English on its
      <a href="index.html#module">module page</a>, and the
      <a href="support.html">support pages</a> answer the most common questions.</p>
    </main>
'''
    desc = ("User manuals for the ClassTiles teacher app — currently available in German only, "
            "readable online and as PDF.")
    return shell.page("en/manuals.html", "Manuals — ClassTiles", desc, body)


def en_ai():
    body = f'''    <div class="pagetitle"><h1>Digitalisation &amp; AI</h1>
      <p>Handbooks and classroom material — German only</p></div>
    <main class="prose">
      <p>Alongside the app there is a growing set of material for teachers who want to use
      digital tools and AI to genuinely lighten their workload — without giving up on
      understanding what these tools actually do.</p>
      <p><strong>All of it is written in German</strong>, because it is built around German
      school practice: the data-protection rules it works from, the way lessons are planned,
      and the wording of the classroom handouts. A translation would need rewriting rather
      than translating, and that is not planned.</p>
      <ul>
        <li><a href="../ki-handbuecher.html">AI handbooks</a> — four volumes on building
        reliable, repeatable AI workflows for lesson preparation and teaching material.</li>
        <li><a href="../ki-material.html">Material for the classroom</a> — three ready-made
        A4 sheets that set out what pupils may use AI for, and how they document it.</li>
      </ul>
      <p>Training sessions for schools are in preparation; the
      <a href="../digitalisierung-ki.html">German page</a> carries the details. There is
      nothing to book yet.</p>
      <p><a href="{MAILTO}">Register your interest by email</a></p>
    </main>
'''
    desc = ("AI handbooks and classroom material for teachers, written in German — plus "
            "training sessions in preparation for German-speaking schools.")
    return shell.page("en/digitalisation-ai.html", "Digitalisation & AI — ClassTiles", desc, body)


def main():
    for name, text in (("digitalisierung-ki.html", de()),
                       ("en/manuals.html", en_manuals()),
                       ("en/digitalisation-ai.html", en_ai())):
        with open(os.path.join(REPO, name), "w", encoding="utf-8") as f:
            f.write(text)
        print("  " + name)


if __name__ == "__main__":
    main()
