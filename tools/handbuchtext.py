#!/usr/bin/env python3
"""Wandelt das Markdown der KI-Handbücher in das HTML der Website.

Die KI-Handbücher entstehen anders als die Modulhandbücher: Quelle ist Markdown im
Instagram-Repo, aus dem die dortige Werkstatt das A4-PDF setzt. Für die Website wird
dasselbe Markdown ein zweites Mal gesetzt — hier für den Bildschirm.

Warum ein zweiter Renderer neben dem der Werkstatt (Node, `marked`): Die beiden setzen
verschiedene Medien und teilen keine einzige CSS-Regel — im Druckbuch wird ein Zitat eine
Randnotiz, hier ein Merksatz über die Textbreite. Vor allem aber ist der gesamte Bau dieses
Repos `python3 tools/…` ohne eine einzige Abhängigkeit; eine npm-Installation dafür wäre
teurer als die 200 Zeilen hier. Gemeinsam ist den beiden Wegen die Quelle, nicht der Renderer.

Deshalb ist die Grammatik bewusst klein und geschlossen — genau das, was in den vier Bänden
tatsächlich vorkommt (ausgezählt, nicht geraten):

    # Titel / # NN · Kapitel      ## Abschnitt        > Merksatz
    - Liste / 1. Liste            | Tabelle |         ~~~text … ~~~
    **fett**  *kursiv*  `code`  [text](ziel)          Zeilenende mit 2 Leerzeichen = <br>

Bilder kommen nicht vor. Alles, was nicht in dieser Liste steht, ist ein Fehler und bricht
den Lauf ab, statt still als Fließtext durchzurutschen.

Die Ankerregel — öffentliche Schnittstelle, wie bei den Modulhandbüchern:

    # 00 · Die sechs Begriffe   →  id="kapitel-00"
    ##  1 · Prompt              →  id="kapitel-00-prompt"
    ##  Die Grenze              →  id="kapitel-00-die-grenze"

Abschnittsanker tragen die Kapitelnummer, weil `## Die Grenze` in jedem Kapitel vorkommt.
Zwei gleiche Anker innerhalb eines Kapitels brechen den Lauf ab: Das Glossar verlinkt diese
Anker, ein still überschriebener Anker wäre ein stiller Fehllink.
"""
import html
import re

# Der Anker soll im Glossar noch lesbar sein. Sechs Wörter reichen, um Abschnitte innerhalb
# eines Kapitels zu unterscheiden — der Rest der Überschrift steht ja auf der Seite.
ANKER_WOERTER = 6

UMLAUTE = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


class Fehler(Exception):
    """Die Quelle enthält etwas, das diese Grammatik nicht kennt."""


def slug(text):
    """Überschrift → Ankerbestandteil. Eine führende Zählnummer entfällt."""
    text = re.sub(r"^\d+\s*·\s*", "", text.strip())
    text = text.lower().translate(UMLAUTE)
    woerter = [w for w in re.split(r"[^a-z0-9]+", text) if w]
    return "-".join(woerter[:ANKER_WOERTER])


def inline(text):
    """Inline-Auszeichnung. Erst escapen, dann auszeichnen — nie umgekehrt."""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def _absatz(zeilen):
    """Mehrere Quellzeilen werden ein Absatz; 2 Leerzeichen am Ende trennen die Zeile.

    Erst zusammensetzen, dann auszeichnen. Zeilenweise auszuzeichnen wäre naheliegend und
    falsch: Die Quelle bricht bei ~95 Zeichen um, und eine Auszeichnung, die dabei über den
    Umbruch läuft (`**Band 2 — „Unterrichtsmaterial selbst\\nbauen“**`), hätte auf keiner
    der beiden Zeilen ein Gegenstück und bliebe als rohes Markdown stehen.
    """
    marke = "\x00br\x00"
    teile = []
    for i, z in enumerate(zeilen):
        teile.append(z.strip())
        teile.append(marke if z.endswith("  ") and i < len(zeilen) - 1 else " ")
    return inline("".join(teile[:-1])).replace(marke, "<br>")


def _ist_blockanfang(z):
    return (z.startswith(("#", ">", "- ", "|", "~~~"))
            or re.match(r"^\d+\.\s", z) is not None)


def _tabelle(zeilen):
    def zellen(z):
        return [t.strip() for t in z.strip().strip("|").split("|")]

    kopf = "".join(f"<th>{inline(t)}</th>" for t in zellen(zeilen[0]))
    rumpf = "".join(
        "<tr>" + "".join(f"<td>{inline(t)}</td>" for t in zellen(z)) + "</tr>"
        for z in zeilen[2:])
    return (f'<div class="tablewrap"><table><thead><tr>{kopf}</tr></thead>'
            f"<tbody>{rumpf}</tbody></table></div>")


def _liste(zeilen, geordnet):
    tag = "ol" if geordnet else "ul"
    muster = r"^\d+\.\s+" if geordnet else r"^-\s+"
    punkte, offen = [], []
    for z in zeilen:
        if re.match(muster, z):
            if offen:
                punkte.append(offen)
            offen = [re.sub(muster, "", z)]
        else:
            offen.append(z.strip())          # Fortsetzung einer umbrochenen Zeile
    punkte.append(offen)
    inhalt = "".join(f"<li>{_absatz(p)}</li>" for p in punkte)
    return f"<{tag}>{inhalt}</{tag}>"


def _bloecke(zeilen, kapitel_nr, anker_je_kapitel):
    """Blockgrammatik. Liefert HTML und sammelt die Abschnittsanker nebenbei ein."""
    aus, abschnitte, i = [], [], 0
    while i < len(zeilen):
        z = zeilen[i]
        if not z.strip():
            i += 1
        elif z.startswith("## "):
            titel = z[3:].strip()
            anker = f"kapitel-{kapitel_nr}-{slug(titel)}" if kapitel_nr else slug(titel)
            if anker in anker_je_kapitel:
                raise Fehler(f"Anker doppelt in Kapitel {kapitel_nr}: #{anker} "
                             f"— zwei Abschnitte heißen gleich ({titel!r})")
            anker_je_kapitel.add(anker)
            abschnitte.append((titel, anker))
            aus.append(f'<h3 id="{anker}">{inline(titel)}</h3>')
            i += 1
        elif z.startswith("#"):
            raise Fehler(f"Überschriftsebene hier nicht erwartet: {z!r}")
        elif z.startswith("~~~"):
            ende = i + 1
            while ende < len(zeilen) and not zeilen[ende].startswith("~~~"):
                ende += 1
            if ende >= len(zeilen):
                raise Fehler(f"Nicht geschlossener ~~~-Block ab {z!r}")
            roh = "\n".join(zeilen[i + 1:ende])
            aus.append(f'<pre class="prompt">{html.escape(roh, quote=False)}</pre>')
            i = ende + 1
        elif z.startswith(">"):
            ende = i
            while ende < len(zeilen) and zeilen[ende].startswith(">"):
                ende += 1
            text = [zeilen[k].lstrip(">").strip() for k in range(i, ende)]
            aus.append(f"<blockquote>{_absatz(text)}</blockquote>")
            i = ende
        elif z.startswith("|"):
            ende = i
            while ende < len(zeilen) and zeilen[ende].startswith("|"):
                ende += 1
            if ende - i < 2 or not re.match(r"^\|[\s:|-]+\|$", zeilen[i + 1].strip()):
                raise Fehler(f"Tabelle ohne Trennzeile ab {z!r}")
            aus.append(_tabelle(zeilen[i:ende]))
            i = ende
        elif z.startswith("- ") or re.match(r"^\d+\.\s", z):
            geordnet = not z.startswith("- ")
            muster = r"^\d+\.\s" if geordnet else r"^-\s"
            ende = i + 1
            while (ende < len(zeilen) and zeilen[ende].strip()
                   and (re.match(muster, zeilen[ende]) or not _ist_blockanfang(zeilen[ende]))):
                ende += 1
            aus.append(_liste(zeilen[i:ende], geordnet))
            i = ende
        else:
            ende = i + 1
            while ende < len(zeilen) and zeilen[ende].strip() and not _ist_blockanfang(zeilen[ende]):
                ende += 1
            aus.append(f"<p>{_absatz(zeilen[i:ende])}</p>")
            i = ende
    return "".join(aus), abschnitte


def fliesstext(text):
    """Markdown ohne Kapitelstruktur — für kurze Texte wie die Einträge unter „Neues".

    Dieselbe Grammatik, nur ohne Kapitel: Abschnittsüberschriften bekommen hier keinen Anker,
    weil ein Eintrag von wenigen Absätzen keinen Sprungpunkt in sich braucht.
    """
    aus, _ = _bloecke(text.split("\n"), None, set())
    return aus


def parse(pfad):
    """Liest ein handbuch.md und liefert Vorspann, Kapitel und den fertigen Textkörper."""
    with open(pfad, encoding="utf-8") as f:
        zeilen = f.read().replace("\t", "    ").split("\n")

    # Aufteilen: alles vor dem ersten Kapitel ist Vorspann. Ein Kapitel erkennt man an der
    # zweistelligen Zählnummer — das unterscheidet „# 00 · …" vom Titel „# KI-Workflows …".
    kapitel_start = [(i, m) for i, z in enumerate(zeilen)
                     if (m := re.match(r"^#\s+(\d{2})\s*·\s*(.+)$", z))]
    if not kapitel_start:
        raise Fehler(f"{pfad}: kein Kapitel „# NN · Titel“ gefunden")

    vorspann = zeilen[:kapitel_start[0][0]]
    meta = _vorspann(vorspann, pfad)

    kapitel, teile, anker_gesamt = [], [], []
    for pos, (start, m) in enumerate(kapitel_start):
        nr, titel = m.group(1), m.group(2).strip()
        ende = kapitel_start[pos + 1][0] if pos + 1 < len(kapitel_start) else len(zeilen)
        anker_je_kapitel = set()
        rumpf, abschnitte = _bloecke(zeilen[start + 1:ende], nr, anker_je_kapitel)
        kapitel.append((nr, titel))
        anker_gesamt += [(nr, t, a) for t, a in abschnitte]
        teile.append(f'<h2 class="chapter" id="kapitel-{nr}">'
                     f'<span class="num">{nr}</span> {inline(titel)}</h2>{rumpf}')

    meta["kapitel"] = kapitel
    meta["abschnitte"] = anker_gesamt
    meta["body"] = "\n".join(teile)
    return meta


def _vorspann(zeilen, pfad):
    """Titel, Claim, Reihenangabe, Merksatz und Standzeile aus dem Kopf der Quelle."""
    text = [z for z in zeilen if z.strip()]
    if not text or not text[0].startswith("# "):
        raise Fehler(f"{pfad}: erste Zeile muss der Titel „# …“ sein")
    if len(text) < 2 or not text[1].startswith("## "):
        raise Fehler(f"{pfad}: nach dem Titel wird der Claim „## …“ erwartet")

    meta = {"titel": text[0][2:].strip(), "claim": text[1][3:].strip(),
            "merksatz": "", "stand": "", "ausgabe": ""}

    rest = zeilen[zeilen.index(text[1]) + 1:]
    stand_zeilen = [z for z in rest if "Stand:" in z and not z.startswith((">", "#"))]
    if not stand_zeilen:
        raise Fehler(f"{pfad}: keine Standzeile („… · Stand: …“) im Vorspann")
    standzeile = stand_zeilen[-1].strip().strip("*")
    felder = [t.strip() for t in standzeile.split("·")]
    meta["stand"] = next(t.split(":", 1)[1].strip() for t in felder if t.startswith("Stand:"))
    meta["ausgabe"] = " · ".join(t for t in felder if not t.startswith("Stand:"))

    merksatz = [z for z in rest if z.startswith(">")]
    if merksatz:
        meta["merksatz"] = _absatz([z.lstrip(">").strip() for z in merksatz])

    # Der Vorlauftext ohne Merksatz und ohne Standzeile ist der Anreißer der Seite.
    anreisser = [z for z in rest if not z.startswith(">") and z.strip() != standzeile
                 and "Stand:" not in z]
    meta["anreisser"], _ = _bloecke(anreisser, None, set())
    return meta
