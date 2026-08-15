#!/usr/bin/env python3
"""Erzeugt ki-kurzfassung-*.html — je Band eine Seite „Das Wichtigste in Kürze".

    python3 tools/pages/ki_kurzfassungen.py

Eine Kurzfassung ist keine zweite, kürzere Fassung des Handbuchs — das wäre ein Text, der
gepflegt werden muss und trotzdem veraltet. Sie ist aus drei Teilen gebaut:

1. Passagen, in denen der Band sich selbst zusammenfasst („Die Idee in einem Satz", „Die
   Methode", „Was hier nicht versprochen wird"). Die werden **wörtlich aus der Quelle
   herausgeschnitten**, nicht abgeschrieben. Sie ändern sich mit dem Band mit.
2. Die Mitnehmpunkte in MITNEHMEN — der einzige selbst geschriebene Teil. Jeder Punkt zeigt
   auf das Kapitel, aus dem er stammt, damit er nachprüfbar bleibt.
3. Die Kapitelkarte, aus der geparsten Quelle.

Dass Teil 1 geschnitten und nicht paraphrasiert wird, ist der Punkt: Eine Zusammenfassung, die
den Sinn verschiebt, ist schlimmer als keine — und beim Umschreiben verschiebt er sich immer.
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

# Je Band: die Ankerpunkte der selbstzusammenfassenden Passagen und die Mitnehmpunkte.
# Die Lesezeit steht bei den Banddaten in ki_handbuecher.py, weil auch das Regal
# und die Handbuchseite sie nennen. Alle drei Passagen sind (Überschrift, Anker): Wie sie
# heißen, entscheidet der Band, nicht diese Datei — Band 4 führt weder „Die Idee in einem
# Satz" noch „Die Methode", und eine erfundene Überschrift über einem wörtlichen Zitat wäre
# genau die Verschiebung, die das Schneiden vermeiden soll.
# Ein Mitnehmpunkt ist (Text, Zielanker) — der Anker darf None sein.
KURZ = {
    "workflows": dict(
        idee=("Die Idee in einem Satz", "kapitel-18-die-idee-in-einem-satz"),
        methode=("Die Methode", "kapitel-01-die-methode"),
        grenzen=("Was der Band nicht verspricht", "kapitel-01-was-hier-nicht-versprochen-wird"),
        mitnehmen=[
            ("Sechs Wörter reichen als Vokabular: Prompt, Kontext, Modell, Halluzination, "
             "Skill, Agent. Sitzen die, liest sich der Rest fast von selbst.", "kapitel-00"),
            ("Mehr Kontext ist nicht besserer Kontext. Jede Angabe gehört an die kleinste "
             "Stelle, an der sie ihren Zweck noch erfüllt.", "kapitel-03"),
            ("Namen, Noten und Diagnosen bleiben draußen, nicht als guter Vorsatz, sondern "
             "als Stoppregel, die wörtlich im Skill steht.", "kapitel-04-die-stoppregel"),
            ("Beschreibe zuerst, wie ein gelungenes Ergebnis aussieht. Ohne Kriterium lässt "
             "sich nichts prüfen, und ohne Prüfung ist der Skill wertlos.", "kapitel-06"),
            ("Drei Phasen statt einer: einmal gemeinsam durchlaufen, den geglückten Durchlauf "
             "festhalten, erst daraus den Skill verdichten.", "kapitel-07"),
            ("Teste einen Skill nie nur mit dem Beispiel, aus dem er entstanden ist; sonst "
             "weißt du nicht, ob er den Ablauf gelernt hat oder das Beispiel.", "kapitel-11"),
            ("Verbessere nur an Fehlern, die du verstanden hast. Jede Regel auf Verdacht ist "
             "der erste Schritt ins Regelchaos.", "kapitel-13"),
        ]),
    "materialwerkstatt": dict(
        idee=("Die Idee in einem Satz", "kapitel-16-die-idee-in-einem-satz"),
        methode=("Die Methode", "kapitel-01-die-methode"),
        grenzen=("Was der Band nicht verspricht", "kapitel-01-was-hier-nicht-versprochen-wird"),
        mitnehmen=[
            ("Gekauftes Material ist selten schlecht; es passt nur nicht. Die Arbeit steckt "
             "nicht im Blatt, sondern in der Beschreibung deines Unterrichts.", "kapitel-01"),
            ("Ein Chat ist ein Gespräch und danach weg. Eine Werkstatt ist ein Ort: Der "
             "Kontext liegt bereit, das Ergebnis bleibt liegen.", "kapitel-02"),
            ("Schulbuchinhalte bleiben draußen. Die Seitenangabe an der Aufgabe leistet "
             "dasselbe, ohne das Urheberrecht zu berühren.", "kapitel-04"),
            ("Vier Orte im Ordner, je einer für eine Sorte Kontext: dauerhaft, für die "
             "Reihe, für die Aufgabe, für heute.", "kapitel-05"),
            ("Die Ankerdatei beschreibt einmal, was in deinem Unterricht immer gilt. Danach "
             "schreibt sich das einzelne Blatt schnell.", "kapitel-06"),
            ("Vier Verbote statt vieler Wünsche: „Erstelle gutes Material“ lässt sich nicht "
             "nachsehen, „Schreib nie außerhalb des Eingangs“ schon.", "kapitel-07"),
            ("Nichts verlässt den Eingang von selbst. Nur du verschiebst; das ist der "
             "Handgriff, an dem die Verantwortung hängt.", "kapitel-11"),
        ]),
    "ablauf": dict(
        idee=("Die Idee in einem Satz", "kapitel-04-die-idee-in-einem-satz"),
        methode=("Die Rechnung", "kapitel-01-die-rechnung"),
        grenzen=("Was der Band nicht behauptet", "kapitel-04-was-dieser-band-nicht-behauptet"),
        mitnehmen=[
            ("Ein langer Prompt ist keine Regel, sondern eine Regel, die du jedes Mal neu "
             "tippst, und beim Tippen leicht veränderst.", "kapitel-01"),
            ("Ein Teil der Schwankung, die man dem Modell zuschreibt, stammt aus der Eingabe. "
             "Was einmal geschrieben dasteht, schwankt nicht.", "kapitel-01-die-rechnung"),
            ("Vier Bausteine sortieren alles: Ankerdatei, was immer gilt · Skill, der "
             "geschriebene Ablauf · Agent, die Erlaubnis zu handeln · Ablauf, die Kette "
             "drumherum.", "kapitel-02"),
            ("Eine einzige Frage entscheidet, wohin eine Angabe gehört: Kommt das wieder?",
             "kapitel-02-die-eine-frage-die-alles-sortiert"),
            ("Im Auftrag bleibt am Ende nur, was heute gilt. Der Rest steht einmal irgendwo "
             "und wird gerufen.", "kapitel-03"),
            ("Das rechnet sich über Wiederholung. Wer KI zweimal im Monat für eine schnelle "
             "Frage nutzt, braucht nichts davon.", "kapitel-00-fuer-wen-das-nichts-ist"),
        ]),
    "uebungsseiten": dict(
        idee=("Was am Ende dasteht", "kapitel-00-was-am-ende-dasteht"),
        methode=("Drei Eigenschaften, die den Alltag entscheiden",
                 "kapitel-01-drei-eigenschaften-die-den-alltag-entscheiden"),
        grenzen=("Zwei Grenzen, die nicht verhandelbar sind",
                 "kapitel-08-zwei-grenzen-die-nicht-verhandelbar-sind"),
        mitnehmen=[
            ("Eine Übungsseite ist eine einzige Datei. Doppelklick, sie läuft im Browser, sie "
             "läuft ohne Internet, und sie sendet nichts.", "kapitel-01"),
            ("Was die Klasse eintippt, bleibt auf ihrem Gerät — auch vor dir. Wer wissen muss, "
             "wer wie weit ist, braucht dafür einen zweiten Weg.",
             "kapitel-01-was-sie-nicht-ist"),
            ("Sechs Angaben machen den Auftrag: Fach und Stoff, wie geübt wird, was nach dem "
             "Prüfen passiert, wie viel, die Form, was draußen bleibt.", "kapitel-03"),
            ("Der Satz, dass alles in eine einzige Datei gehört und nichts nachgeladen wird, "
             "steht in jedem Auftrag. Ohne ihn ist die Seite im Raum ohne WLAN weiß.",
             "kapitel-01"),
            ("Erst die Fachaufgaben prüfen, dann schmücken. Punkte, Stufen und Bestenliste "
             "kommen in einer zweiten Runde dazu.", "kapitel-04"),
            ("Die Bestenliste steht auf dem Gerät, nicht über der Klasse. „Lässt sich "
             "zurücksetzen“ ist daran der wichtigste Halbsatz.",
             "kapitel-04-die-bestenliste-vergleicht-kein-klassenzimmer"),
            ("Je älter die Lerngruppe, desto weniger trägt die Punktzahl: Statt richtig oder "
             "falsch verlangst du einen Satz, der die Entscheidung erklärt.", "kapitel-05"),
            ("Vor dem Weitergeben einmal selbst durchspielen, auch absichtlich falsch, und die "
             "Seite ohne WLAN öffnen.", "kapitel-08"),
        ]),
    "assistent": dict(
        idee=("Die Idee in einem Satz", "kapitel-16-die-idee-in-einem-satz"),
        methode=("Das Grundprinzip", "kapitel-01-das-grundprinzip"),
        grenzen=("Was KI nicht übernimmt", "kapitel-01-was-ki-nicht-uebernimmt"),
        mitnehmen=[
            ("Fünf Ebenen tragen das Ganze: Profil, Projekt, Workflow, Entwurf, Prüfung; "
             "und die wichtigste Trennung liegt zwischen den letzten beiden.", "kapitel-03"),
            ("Die Datenampel kommt vor den ersten Prompt. Die Frage ist nicht, ob die KI es "
             "kann, sondern ob sie es sehen darf.", "kapitel-02"),
            ("Das Lehrkräfteprofil ist datensparsam: Schulform, Fächer, Arbeitsprinzipien, "
             "keine Klasse, kein Name, keine Diagnose.", "kapitel-04"),
            ("Fünf fertige Workflows liegen zum Übernehmen bereit, vom Unterrichtsarchitekten "
             "bis zum Vertretungs-Paket.", "kapitel-06-fuenf-workflows-in-diesem-workbook"),
            ("Der Einstieg dauert 15 Minuten und beginnt mit einem einzigen Workflow, nicht "
             "mit fünf.", "kapitel-14"),
        ]),
}


def abschnitt(body, anker, quelle):
    """Schneidet einen Abschnitt wörtlich aus dem Band — Inhalt bis zur nächsten Überschrift."""
    treffer = re.search(rf'<h([23]) id="{re.escape(anker)}">(.*?)</h\1>', body)
    if not treffer:
        sys.exit(f"Kurzfassung {quelle}: Abschnitt #{anker} nicht gefunden")
    rest = body[treffer.end():]
    ende = re.search(r"<h[23][ >]", rest)
    text = rest[:ende.start()] if ende else rest
    # „Die Idee in einem Satz" ist in jedem Band der letzte Abschnitt, und danach folgt keine
    # Überschrift mehr, sondern das Kolophon („Band 3 · Ausgabe 1 · Redaktionsstand: …").
    # Es gehört zur Quelle, ist aber keine Aussage — hier stünde es sonst mitten im Zitat.
    # Ohne re.I greift das Muster nicht: der Vorspann schreibt „Stand:", das Kolophon
    # „Redaktionsstand:".
    return re.sub(r"<p>(?:<b>)?[^<]*stand:[^<]*(?:</b>)?</p>\s*$", "", text, flags=re.I)


def seite(b, m, k):
    body_q = m["body"]
    i_titel, i_anker = k["idee"]
    m_titel, m_anker = k["methode"]
    g_titel, g_anker = k["grenzen"]

    punkte = "".join(
        f'<li>{html.escape(t)}'
        + (f' <a class="beleg" href="ki-handbuch-{b["slug"]}.html#{a}">Kap.&nbsp;'
           f'{a.split("-")[1]}</a>' if a else "")
        + "</li>"
        for t, a in k["mitnehmen"])

    kapitel = "".join(
        f'<li><a href="ki-handbuch-{b["slug"]}.html#kapitel-{nr}" data-nr="{nr}">'
        f"{html.escape(t)}</a></li>" for nr, t in m["kapitel"])

    lesen = f'ki-handbuch-{b["slug"]}.html'
    body = f'''    <a class="back" href="ki-handbuecher.html">← Alle KI-Handbücher</a>
    <div class="hbhead ki" style="--c:var(--navy)">
      <div>
        <div class="eyebrow">Kurzfassung · {html.escape(b["reihe"])} · {html.escape(b["zaehler"])}</div>
        <h1>{html.escape(m["titel"])}</h1>
        <p class="claim">{html.escape(m["claim"])}</p>
      </div>
    </div>
    <div class="hbmeta">
      <span><b>Lesezeit</b> {b["kurz_minuten"]} Minuten</span>
      <span><b>Statt</b> {len(m["kapitel"])} Kapitel im Volltext</span>
      <span><b>Stand</b> {html.escape(m["stand"])}</span>
    </div>
    <div class="cta" style="margin-top:20px">
      <a class="btn b-solid" href="{lesen}">Ganzes Handbuch lesen</a>
      <a class="btn b-line" href="assets/ki/{b["pdf"]}" download>PDF laden</a>
    </div>

    <div class="kurz">
      <blockquote>{m["merksatz"]}</blockquote>

      <h2>{html.escape(i_titel)}</h2>
      <div class="zitat">{abschnitt(body_q, i_anker, b["slug"])}
        <p class="quelle"><a href="{lesen}#{i_anker}">im Handbuch nachlesen →</a></p></div>

      <h2>{html.escape(m_titel)}</h2>
      <div class="zitat">{abschnitt(body_q, m_anker, b["slug"])}
        <p class="quelle"><a href="{lesen}#{m_anker}">im Handbuch nachlesen →</a></p></div>

      <h2>Was du mitnimmst</h2>
      <ol class="mitnehmen">{punkte}</ol>

      <h2>{html.escape(g_titel)}</h2>
      <div class="zitat warn">{abschnitt(body_q, g_anker, b["slug"])}
        <p class="quelle"><a href="{lesen}#{g_anker}">im Handbuch nachlesen →</a></p></div>

      <h2>Die {len(m["kapitel"])} Kapitel</h2>
      <ol class="kapitelkarte">{kapitel}</ol>

      <div class="cta" style="margin-top:30px">
        <a class="btn b-solid" href="{lesen}">Ganzes Handbuch lesen</a>
        <a class="btn b-line" href="ki-glossar.html">Begriffe nachschlagen</a>
      </div>
    </div>
'''
    titel = f'{m["titel"]} — Kurzfassung — ClassTiles'
    desc = (f'Das Wichtigste aus „{m["titel"]}" in {b["kurz_minuten"]} Minuten: die Idee in einem '
            f'Satz, die Methode, {len(k["mitnehmen"])} Punkte zum Mitnehmen und die Grenzen '
            f'des Bandes.')
    return shell.page(f"ki-kurzfassung-{b['slug']}.html", titel, desc, body)


def main():
    for b in kh.BAENDE:
        if not b["quelle"] or not b.get("kurz_minuten"):
            continue          # das Cowork-Heft führt die nötigen Abschnitte nicht
        if b["slug"] not in KURZ:
            sys.exit(f"Kurzfassung fehlt für Band {b['slug']!r}")
        m = handbuchtext.parse(os.path.join(REPO, b["quelle"]))
        k = KURZ[b["slug"]]
        with open(os.path.join(REPO, f"ki-kurzfassung-{b['slug']}.html"), "w",
                  encoding="utf-8") as f:
            f.write(seite(b, m, k))
        print(f'  ki-kurzfassung-{b["slug"]}.html — {len(k["mitnehmen"])} Punkte, '
              f'{b["kurz_minuten"]} Min statt {len(m["kapitel"])} Kapitel')


if __name__ == "__main__":
    main()
