#!/usr/bin/env python3
"""Erzeugt ki-glossar.html — die Begriffe der KI-Handbücher mit Sprung an ihre Fundstelle.

    python3 tools/pages/ki_glossar.py

Das Glossar erklärt nur, was in den Bänden auch vorkommt. Jeder Eintrag hat mindestens ein
Linkziel; ein Eintrag ohne Beleg wäre Wissen, das nirgends steht und niemand pflegt.

Die Beschriftung der Links wird nicht hier geschrieben, sondern aus den Bänden abgeleitet:
„Band 1 · Kap. 00 · Prompt" entsteht aus der geparsten Quelle. Wird ein Kapitel umbenannt,
stimmt das Glossar beim nächsten Bau von selbst wieder — und zeigt ein Ziel nicht mehr auf
einen vorhandenen Anker, bricht der Lauf ab, statt einen toten Link zu schreiben.
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import handbuchtext  # noqa: E402
import ki_handbuecher as kh  # noqa: E402
import shell  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HUB = "digitalisierung-ki.html"

# „6 · Agent" → „Agent". Die Zählnummer ordnet den Abschnitt innerhalb seines Kapitels und
# sagt im Glossar nichts.
ZAEHLNUMMER = re.compile(r"^\d+\s*·\s*")

# `satz` ist eine echte Definition: Sie sagt, was der Begriff bezeichnet, und ist ohne den Band
# verständlich. Das ist der Unterschied zum `merksatz` — den führen elf Einträge zusätzlich,
# weil die Quelle ihn führt („Darf selbst handeln. Deshalb die Stoppregeln."). Ein Merksatz ist
# eine Eselsbrücke für jemanden, der die Sache schon kennt, und taugt deshalb nicht als
# Definition; er steht auf der Seite unter ihr, nicht an ihrer Stelle.
# `auch` verweist auf einen verwandten Eintrag desselben Glossars.
GLOSSAR = [
    dict(begriff="Ablauf", auch="Workflow",
         satz="Die vollständige Kette einer wiederkehrenden Aufgabe: der Auslöser, die "
              "einzelnen Schritte, die beteiligten Bausteine und die Prüfung am Ende. Der "
              "Ablauf ist der Bauplan, in dem Ankerdatei, Skill und Agent ihren Platz haben.",
         ziele=[("ablauf", "kapitel-02-ablauf-die-kette-drumherum")]),
    dict(begriff="Agent",
         satz="Ein KI-Werkzeug, das eine Aufgabe selbst in Arbeitsschritte zerlegt und diese "
              "nacheinander ausführt, ohne zwischen den Schritten auf eine Freigabe zu warten. "
              "Weil es dabei auch Dateien anlegen und verändern kann, braucht es Stoppregeln.",
         merksatz="Darf selbst handeln. Deshalb die Stoppregeln.",
         ziele=[("workflows", "kapitel-00-agent"),
                ("ablauf", "kapitel-02-agent-die-erlaubnis-zu-handeln")]),
    dict(begriff="Ankerdatei",
         satz="Eine einfache Textdatei mit den Angaben, die in deinem Unterricht dauerhaft "
              "gelten: Schulform und Bundesland, Fächer und Jahrgänge, deine Standards für ein "
              "Arbeitsblatt und deine Verbote. Sie wird einmal geschrieben und danach von jedem "
              "Ablauf mitgelesen, statt in jedem Auftrag wiederholt zu werden.",
         ziele=[("ablauf", "kapitel-02-ankerdatei-der-rahmen-der-immer-gilt"),
                ("materialwerkstatt", "kapitel-06")]),
    dict(begriff="Arbeitsauftrag-Check",
         satz="Der Beispiel-Skill, an dem Band 1 den ganzen Weg einmal vorführt, von einer "
              "wiederkehrenden Aufgabe bis zum getesteten Skill. Er prüft einen Arbeitsauftrag, "
              "bevor er in den Unterricht geht.",
         ziele=[("workflows", "kapitel-14")]),
    dict(begriff="Datenampel", auch="Stoppregel",
         satz="Ein Schema in drei Stufen, das vor jeder Eingabe klärt, welche Angaben ein "
              "KI-Werkzeug sehen darf: Grün ist in der Regel unkritisch, Gelb erfordert eine "
              "vorherige Klärung, Rot gehört grundsätzlich nicht hinein. Es ersetzt die Frage "
              "„Kann die KI das?“ durch „Darf sie das sehen?“.",
         ziele=[("assistent", "kapitel-02"), ("workflows", "kapitel-04"),
                ("materialwerkstatt", "kapitel-03")]),
    dict(begriff="Dreifach-Test",
         satz="Ein Prüfverfahren für fertige Skills: Der Skill läuft einmal mit einem "
              "typischen Fall, einmal mit fehlenden Angaben und einmal mit einem Grenzfall. "
              "Erst wenn er alle drei besteht, hat er den Ablauf gelernt und nicht nur das "
              "Beispiel.",
         merksatz="Teste einen Skill nie nur mit dem Beispiel, aus dem er entstanden ist.",
         ziele=[("workflows", "kapitel-11")]),
    dict(begriff="Eingang", auch="Freigabeordner",
         satz="Der einzige Ordner, in den ein KI-Werkzeug schreiben darf. Alles Erzeugte landet "
              "dort und bleibt liegen, bis du es gesichtet und selbst weiterverschoben hast.",
         ziele=[("materialwerkstatt", "kapitel-05"), ("materialwerkstatt", "kapitel-11")]),
    dict(begriff="Entscheidungslog",
         satz="Die Mitschrift der Entscheidungen aus einem geglückten Durchlauf: welche "
              "Rückfrage unverzichtbar war, welche Annahme sich als falsch erwies, welche "
              "Korrektur das Ergebnis verbessert hat und welche Reihenfolge nicht verändert "
              "werden darf. Aus ihr entsteht später der Skill.",
         ziele=[("workflows", "kapitel-08-entscheidungslog")]),
    dict(begriff="Entwurf", auch="Prüfung",
         satz="Das Zwischenergebnis, das die KI liefert, strukturiert und prüfbar, aber noch "
              "keine pädagogische Entscheidung. Ein brauchbarer Entwurf macht seine Annahmen, "
              "Unsicherheiten und fehlenden Angaben sichtbar.",
         ziele=[("assistent", "kapitel-03-4-entwurf-was-liefert-die-ki")]),
    dict(begriff="Ergebnis-Canvas",
         satz="Ein Formular, das vor dem ersten Prompt ausgefüllt wird: Name des Workflows, "
              "Auslöser, nötige Eingaben, gewünschtes Endprodukt und die Kriterien, an denen "
              "ein gelungenes Ergebnis zu erkennen ist.",
         ziele=[("workflows", "kapitel-06-ergebnis-canvas")]),
    dict(begriff="Erfolgsprotokoll",
         satz="Die Aufzeichnung eines Durchlaufs, der funktioniert hat, Schritt für Schritt "
              "mit Eingabe, getroffener Entscheidung, akzeptiertem Ergebnis und Prüfkriterium. "
              "Sie ist das Rohmaterial, aus dem ein Skill verdichtet wird.",
         ziele=[("workflows", "kapitel-08-erfolgsprotokoll")]),
    dict(begriff="Freigabeordner", auch="Eingang",
         satz="Die Regel, dass keine erzeugte Datei den Eingang von selbst verlässt: Du sichtest, "
              "was dort liegt, und verschiebst nur, was du freigibst. Dieser eine Handgriff ist "
              "die Stelle, an der die Verantwortung bei dir bleibt.",
         merksatz="Alles Erzeugte landet im Eingang und bleibt dort. Nur du verschiebst.",
         ziele=[("materialwerkstatt", "kapitel-11")]),
    dict(begriff="Halluzination",
         satz="Eine erfundene Angabe, die das Modell im selben sicheren Ton vorträgt wie eine "
              "belegte: eine Quelle, eine Zahl, eine Vorschrift, die es so nicht gibt. Der "
              "Ausgabe ist das nicht anzusehen; erkennbar wird es erst beim Nachschlagen.",
         merksatz="Erfindet im selben Ton, in dem es zitiert.",
         ziele=[("workflows", "kapitel-00-halluzination")]),
    dict(begriff="Kontext", auch="Kontextfilter",
         satz="Die Angaben, die du einem KI-Werkzeug zu einer Aufgabe mitgibst, damit es sie "
              "sinnvoll bearbeiten kann: Fach, Jahrgang, Stand der Reihe, Zeitrahmen, "
              "Vorwissen. Gemeint ist nicht alles, was du weißt, sondern das, was ohne dich "
              "nicht herauszufinden ist.",
         merksatz="Die Einweisung für die Vertretung. Nicht alles, was du weißt.",
         ziele=[("workflows", "kapitel-00-kontext"), ("workflows", "kapitel-02")]),
    dict(begriff="Kontextfilter",
         satz="Fünf Fragen, die vor jeder Angabe klären, wohin sie gehört: dauerhaft ins "
              "Profil, in das Projekt, in den Skill, nur in den heutigen Auftrag oder gar "
              "nicht hinein.",
         merksatz="Ordne jede Information an die kleinste Stelle, an der sie noch ihren "
                  "Zweck erfüllt.",
         ziele=[("workflows", "kapitel-03")]),
    dict(begriff="Modell",
         satz="Das Sprachmodell hinter einem KI-Werkzeug. Es hat sehr viel Text gelesen, führt "
              "aber kein Gedächtnis über das einzelne Gespräch hinaus, kennt deine Schule und "
              "deine Lerngruppe nicht und lernt aus deinen Korrekturen nichts dazu.",
         merksatz="Sehr belesen. Kein Gedächtnis. Kennt deine Schule nicht.",
         ziele=[("workflows", "kapitel-00-modell")]),
    dict(begriff="Profil",
         satz="Die dauerhafte Beschreibung deines beruflichen Rahmens: Schulform, Bundesland, "
              "Fächer, Jahrgänge, Arbeitsprinzipien. Weil es für alle Projekte gilt, enthält es "
              "keine Klassen, keine Namen und keine Diagnosen.",
         ziele=[("assistent", "kapitel-03-1-profil-wer-bin-ich-beruflich"),
                ("assistent", "kapitel-04"), ("workflows", "kapitel-02-fuer-dich-dauerhaft")]),
    dict(begriff="Projekt", auch="Reihenplan",
         satz="Der Kontext einer einzelnen Unterrichtsreihe: Thema, Zeitraum, Lernprodukt, "
              "Rahmenbedingungen. Er gilt, solange die Reihe läuft, und wird danach abgelegt; "
              "darin unterscheidet er sich vom Profil.",
         ziele=[("assistent", "kapitel-03-2-projekt-woran-arbeite-ich-gerade"),
                ("assistent", "kapitel-05"), ("workflows", "kapitel-02-fuer-ein-projekt")]),
    dict(begriff="Prompt",
         satz="Der Auftrag, den du einem KI-Werkzeug gibst: was zu tun ist, womit, in welcher "
              "Form und woran zu erkennen ist, dass es fertig ist. Anders als ein Suchbegriff "
              "benennt er nicht ein Thema, sondern eine Arbeit.",
         merksatz="Ein Arbeitsauftrag. Kein Suchbegriff.",
         ziele=[("workflows", "kapitel-00-prompt"), ("ablauf", "kapitel-01")]),
    dict(begriff="Prüfung", auch="Entwurf",
         satz="Der Schritt, in dem du den Entwurf der KI fachlich und pädagogisch "
              "verantwortest, bevor er in den Unterricht geht. Er lässt sich nicht an das "
              "Werkzeug abgeben, weil die Verantwortung für das Ergebnis bei dir bleibt.",
         ziele=[("assistent", "kapitel-03-5-pruefung-was-verantwortest-du"),
                ("materialwerkstatt", "kapitel-13")]),
    dict(begriff="Reihenplan", auch="Projekt",
         satz="Die Beschreibung einer Unterrichtsreihe als Zielrahmen statt als Stundenfolge: "
              "was am Ende gekonnt werden soll, welche Etappen dorthin führen, wieviel Zeit zur "
              "Verfügung steht. Eine feste Liste von Stunde 1 bis 12 ist nach zwei Wochen "
              "überholt, ein Zielrahmen nicht.",
         ziele=[("materialwerkstatt", "kapitel-09")]),
    dict(begriff="Skill",
         satz="Ein festgeschriebener Ablauf, den ein KI-Werkzeug auf Abruf ausführt: Er hält "
              "fest, welche Schritte in welcher Reihenfolge nötig sind, welche Eingaben sie "
              "brauchen und woran das Ergebnis geprüft wird. Einmal geschrieben, ersetzt er die "
              "Erklärung, die sonst in jedem Auftrag stünde.",
         merksatz="Ein Ablauf, den du einmal erklärst statt jedes Mal.",
         ziele=[("workflows", "kapitel-00-skill"),
                ("ablauf", "kapitel-02-skill-der-geschriebene-ablauf"),
                ("workflows", "kapitel-09")]),
    dict(begriff="Skill-Bauplan",
         satz="Das Raster, nach dem ein Skill aufgebaut wird: Name, Beschreibung und Auslöser, "
              "zwingende Eingaben, Schritte, Prüfkriterien und Stoppregeln. Es gilt unabhängig "
              "davon, ob dein Werkzeug echte Skill-Dateien kennt, gespeicherte Prompts anbietet "
              "oder nur ein Feld für eigene Anweisungen hat.",
         ziele=[("workflows", "kapitel-10")]),
    dict(begriff="Startprompt",
         satz="Der Auftrag, mit dem der erste begleitete Durchlauf beginnt. Er fordert die KI "
              "ausdrücklich auf, noch nichts zu automatisieren, sondern schrittweise "
              "vorzugehen: erst nach Ziel, Zielgruppe, Eingaben und Qualitätskriterien fragen, "
              "dann einen Schritt vorschlagen, begründen und ausführen.",
         ziele=[("workflows", "kapitel-07-der-startprompt")]),
    dict(begriff="Stoppregel", auch="Datenampel",
         satz="Eine Anweisung, die wörtlich in jedem Skill steht: Das Werkzeug hält an, sobald "
              "ein Auftrag personenbezogene, vertrauliche oder nicht eindeutig freigegebene "
              "Daten enthält, benennt die Datenkategorie, verarbeitet sie nicht weiter und "
              "schlägt eine datensparsame Alternative vor.",
         ziele=[("workflows", "kapitel-04-die-stoppregel"),
                ("materialwerkstatt", "kapitel-03-die-stoppregel")]),
    dict(begriff="Stundenanatomie",
         satz="Das Raster, mit dem du beschreibst, wie deine Stunden gebaut sind: welche Phasen "
              "es gibt, wie lang sie dauern, welche Sozialformen dazugehören. Ohne Phasenangabe "
              "ist nicht zu beurteilen, ob ein Blatt zehn oder dreißig Minuten trägt, ob es "
              "öffnet oder sichert.",
         merksatz="Ein Arbeitsblatt ist immer ein Blatt für eine Phase.",
         ziele=[("materialwerkstatt", "kapitel-08")]),
    dict(begriff="Verbote",
         satz="Negativ formulierte Regeln, die festlegen, was ein Ablauf nicht tun darf. Sie "
              "werden Wünschen vorgezogen, weil ein Verbot überprüfbar ist: man sieht nach und "
              "weiß es.",
         merksatz="Ein Wunsch ist nicht prüfbar, ein Verbot schon.",
         ziele=[("materialwerkstatt", "kapitel-07")]),
    dict(begriff="Werkstatt",
         satz="Eine Arbeitsumgebung, in der Kontext und Ergebnisse an einem festen Ort liegen "
              "bleiben, statt mit dem Gespräch zu verschwinden. Anders als im Chat bringst du "
              "den Kontext nicht jedes Mal mit: Er liegt schon bereit, und das Erzeugte bleibt "
              "liegen, bis du es abholst.",
         ziele=[("materialwerkstatt", "kapitel-02")]),
    dict(begriff="Workflow", auch="Ablauf",
         satz="Die englische Bezeichnung für den Ablauf. Im Workbook meint Workflow zusätzlich "
              "die einzelne festgelegte Arbeitsanweisung für eine wiederkehrende Aufgabe, mit "
              "Auslöser, Eingaben, Schritten und Prüfkriterien.",
         ziele=[("assistent", "kapitel-03-3-workflow-wie-soll-eine-aufgabe"),
                ("assistent", "kapitel-06")]),
]


def baende_lesen():
    """slug → (Bandangabe, {Anker: Beschriftung}). Die Beschriftung nennt Kapitel und Abschnitt."""
    aus = {}
    for b in kh.BAENDE:
        if not b["quelle"]:
            continue
        m = kh.lies(b, nur_struktur=True)
        kapitel = dict(m["kapitel"])
        anker = {f"kapitel-{nr}": f"Kap. {nr} · {titel}" for nr, titel in m["kapitel"]}
        for nr, titel, a in m["abschnitte"]:
            # Beim Abschnittsziel entfällt der Kapiteltitel: Der Abschnitt ist die genauere
            # Angabe, und beides nebeneinander ergäbe Beschriftungen von halber Zeilenlänge.
            # Die führende Zählnummer („6 · Agent") ist im Glossar ebenfalls nur Rauschen.
            anker[a] = f"Kap. {nr} — {ZAEHLNUMMER.sub('', titel)}"
        aus[b["slug"]] = (b["zaehler"], anker)
    return aus


def ziel_link(slug, anker, baende):
    if slug not in baende:
        sys.exit(f"Glossar: unbekannter Band {slug!r}")
    zaehler, anker_map = baende[slug]
    if anker not in anker_map:
        sys.exit(f"Glossar: Anker #{anker} gibt es in Band {slug!r} nicht — "
                 f"wurde ein Kapitel umbenannt?")
    return (f'<a href="ki-handbuch-{slug}.html#{anker}">{zaehler} · '
            f'{html.escape(anker_map[anker])}</a>')


def eintrag(g, baende):
    links = "".join(f"<li>{ziel_link(s, a, baende)}</li>" for s, a in g["ziele"])
    auch = (f'<p class="auch">siehe auch <a href="#begriff-{handbuchtext.slug(g["auch"])}">'
            f'{html.escape(g["auch"])}</a></p>') if g.get("auch") else ""
    # Der Merksatz steht unter der Definition, nicht an ihrer Stelle: Er ist eine Eselsbrücke
    # und erklärt den Begriff niemandem, der ihn noch nicht kennt.
    merk = (f'<p class="merk">{html.escape(g["merksatz"])}</p>') if g.get("merksatz") else ""
    return (f'<div class="gloss" id="begriff-{handbuchtext.slug(g["begriff"])}">'
            f'<h3>{html.escape(g["begriff"])}</h3>'
            f'<p>{html.escape(g["satz"])}</p>{merk}'
            f'<ul class="glossziele">{links}</ul>{auch}</div>')


def seite():
    baende = baende_lesen()
    eintraege = sorted(GLOSSAR, key=lambda g: g["begriff"].lower())

    bekannt = {g["begriff"] for g in eintraege}
    for g in eintraege:
        if g.get("auch") and g["auch"] not in bekannt:
            sys.exit(f'Glossar: „{g["begriff"]}" verweist auf „{g["auch"]}" — den gibt es nicht')

    bloecke, buchstaben = [], []
    for g in eintraege:
        anfang = g["begriff"][0].upper()
        if anfang not in buchstaben:
            buchstaben.append(anfang)
            bloecke.append(f'<h2 class="glossletter" id="buchstabe-{anfang}">{anfang}</h2>')
        bloecke.append(eintrag(g, baende))

    chips = "".join(f'<a href="#buchstabe-{b}">{b}</a>' for b in buchstaben)
    body = f'''    <a class="back" href="{HUB}">← Digitalisierung &amp; KI</a>
    <div class="pagetitle" style="max-width:none">
      <div class="eyebrow">Glossar</div>
      <h1>Die Wörter, die überall vorausgesetzt werden</h1>
      <p class="mlead">{len(eintraege)} Begriffe aus den KI-Handbüchern, jeder so erklärt,
      dass er ohne den Band verständlich ist, und darunter der Sprung an die Stelle, an der es
      ausführlich wird. Was hier steht, steht auch in einem Band; erfunden ist nichts.</p>
    </div>

    <nav class="glossaz" aria-label="Anfangsbuchstaben">{chips}</nav>

    <section style="padding:8px 0 0">
{chr(10).join("      " + b for b in bloecke)}
    </section>

    <section class="rev">
      <p class="note">Ein Begriff fehlt? Die Bände sind die Quelle: Was dort nicht vorkommt,
      steht bewusst auch hier nicht. <a href="ki-handbuecher.html">Zu den Handbüchern</a></p>
    </section>
'''
    desc = (f"Glossar zu KI im Unterricht: {len(eintraege)} Begriffe von Prompt bis Stoppregel, "
            f"verständlich erklärt, mit Sprung an die Fundstelle im Handbuch.")
    return shell.page("ki-glossar.html", "Glossar — ClassTiles", desc, body)


def main():
    text = seite()
    with open(os.path.join(REPO, "ki-glossar.html"), "w", encoding="utf-8") as f:
        f.write(text)
    ziele = sum(len(g["ziele"]) for g in GLOSSAR)
    print(f"  ki-glossar.html — {len(GLOSSAR)} Begriffe, {ziele} Ziele")


if __name__ == "__main__":
    main()
