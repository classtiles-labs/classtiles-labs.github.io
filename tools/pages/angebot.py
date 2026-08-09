#!/usr/bin/env python3
"""Erzeugt digitalisierung-ki.html sowie die beiden englischen Hinweisseiten.

    python3 tools/pages/angebot.py

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


def de():
    themen = "".join(
        f'<div class="mod" style="--c:var(--{f})"><b>{t}</b><span>{x}</span>'
        f'<em>In Vorbereitung</em></div>' for f, t, x in THEMEN)
    formate = "".join(f'<div class="panel"><h3>{t}</h3><p>{x}</p></div>' for t, x in FORMATE)
    body = f'''    <div class="pagetitle" style="max-width:none">
      <div class="eyebrow">In Vorbereitung</div>
      <h1>Digitalisierung &amp; KI</h1>
      <p class="mlead">Nicht mehr digital arbeiten, sondern smarter. Neben der App entstehen
      Fortbildungen und Material für Lehrkräfte, die ihren Alltag mit digitalen Werkzeugen und
      KI spürbar entlasten wollen — ohne den Anspruch aufzugeben, zu verstehen, was da passiert.</p>
    </div>

    <section style="padding:38px 0 0">
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
        <h2>Woran gearbeitet wird</h2>
        <p>Drei Themen, die in der Praxis am häufigsten gefragt werden.</p>
      </div>
      <div class="grid">{themen}</div>
    </section>

    <section class="rev">
      <div class="head">
        <h2>In welcher Form</h2>
      </div>
      <div class="two">{formate}</div>
      <p class="note"><b>Noch gibt es nichts zu buchen.</b> Wenn eines der Themen für dich oder
      dein Kollegium interessant ist, schreib mir — dann melde ich mich, sobald es so weit ist,
      und weiß, woran wirklich Bedarf besteht.</p>
      <div class="cta">
        <a class="btn b-solid" href="{MAILTO}">Interesse anmelden</a>
        <a class="btn b-line" href="handbuecher.html">Zu den Handbüchern</a>
      </div>
    </section>
'''
    desc = ("Fortbildungen, Workshops und Material zu Digitalisierung und KI im Unterricht — "
            "in Vorbereitung. Von der Lehrkraft hinter der App ClassTiles.")
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
      <p>In preparation</p></div>
    <main class="prose">
      <p>Alongside the app, training sessions and materials are being prepared for teachers who
      want to use digital tools and AI to genuinely lighten their workload — without giving up on
      understanding what these tools actually do.</p>
      <p>Three topics are in the works: preparing lessons with AI, the legal and data-protection
      side of AI in schools, and a properly digital teaching routine.</p>
      <p><strong>These offerings are aimed at German-speaking schools</strong>, so the
      <a href="../digitalisierung-ki.html">German page</a> carries the details. There is nothing to
      book yet.</p>
      <p><a href="{MAILTO}">Register your interest by email</a></p>
    </main>
'''
    desc = ("Training and materials on digitalisation and AI in the classroom — in preparation, "
            "aimed at German-speaking schools.")
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
