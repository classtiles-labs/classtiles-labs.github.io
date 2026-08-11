#!/usr/bin/env python3
"""Liest das Claude-Cowork-Heft und liefert dasselbe wie handbuchtext.parse().

Das Heft ist der einzige KI-Titel, dessen Quelle kein Markdown ist, sondern fertig gesetztes
Druck-HTML mit eingebetteten Bildern. Statt eines zweiten Seitenbauers gibt dieses Modul
deshalb genau die Felder zurück, die `ki_handbuecher.band_seite()` ohnehin erwartet — die
Leseseite entsteht danach auf demselben Weg wie bei den vier Markdown-Bänden.

Zwei Dinge werden dabei umgeschrieben:

* **Anker.** Die Quelle nummeriert `id="c01"`, der KI-Bereich `id="kapitel-01"`. Die zweite
  Form gilt, weil Glossar und Kurzfassungen sie voraussetzen — eine Ausnahme für ein einzelnes
  Heft wäre genau die Sorte Sonderfall, über die man in einem Jahr stolpert.
* **Bilder.** Die 17 Bildschirmfotos stecken als Base64-PNG im Dokument und machen es 2,8 MB
  groß. Sie werden herausgelöst und wie bei den Modulhandbüchern nach WebP gewandelt; die
  Seite lädt sie danach einzeln und verzögert.

`div.keep` ist reine Druckanweisung (halte Bild und Text zusammen) und wird aufgelöst.
"""
import base64
import html
import os
import re
import subprocess
import tempfile

MAX_PX = 1800


class Fehler(Exception):
    """Die Quelle sieht anders aus als erwartet."""


def _text(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(s))).strip()


def _bild_masse(pfad):
    aus = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", pfad],
                         capture_output=True, text=True).stdout
    breit = re.search(r"pixelWidth: (\d+)", aus)
    hoch = re.search(r"pixelHeight: (\d+)", aus)
    if not (breit and hoch):
        # Tritt auf, wenn die Base64-Daten kein Bild sind. Ohne diese Meldung stirbt der Lauf
        # an einem AttributeError, der nichts über die Ursache sagt.
        raise Fehler("sips erkennt die eingebetteten Daten nicht als Bild")
    return int(breit.group(1)), int(hoch.group(1))


def _bilder(body, zielordner, webpfad):
    """Base64-PNG → WebP-Datei. Liefert den Rumpf mit umgebogenen src-Angaben."""
    os.makedirs(zielordner, exist_ok=True)
    zaehler = [0]

    def eins(m):
        zaehler[0] += 1
        name = f"bild-{zaehler[0]:02d}.webp"
        ziel = os.path.join(zielordner, name)
        with tempfile.TemporaryDirectory() as tmp:
            roh = os.path.join(tmp, "b.png")
            with open(roh, "wb") as f:
                f.write(base64.b64decode(m.group("daten")))
            breit, hoch = _bild_masse(roh)
            if max(breit, hoch) > MAX_PX:
                # sips -Z setzt die längere Kante exakt auf den Wert, auch nach oben —
                # deshalb nur skalieren, wenn das Original wirklich größer ist.
                subprocess.run(["sips", "-Z", str(MAX_PX), roh, "--out", roh],
                               check=True, capture_output=True)
                breit, hoch = _bild_masse(roh)
            subprocess.run(["cwebp", "-q", "82", "-m", "6", "-quiet", roh, "-o", ziel],
                           check=True)
        return (f'<img src="{webpfad}/{name}" width="{breit}" height="{hoch}" '
                f'loading="lazy" alt="{html.escape(m.group("alt"), quote=True)}">')

    neu, anzahl = re.subn(
        r'<img\s+src="data:image/png;base64,(?P<daten>[^"]+)"\s+alt="(?P<alt>[^"]*)"\s*/?>',
        eins, body)
    if not anzahl:
        raise Fehler("keine eingebetteten Bilder gefunden — hat sich die Quelle geändert?")
    if "base64," in neu:
        raise Fehler("es sind Base64-Daten übrig geblieben")
    return neu, anzahl


def _keep_aufloesen(rumpf):
    """`div.keep` hält im Druck Bild und Text zusammen und hat im Web keine Aufgabe.

    Die Klasse umschließt nie ein weiteres <div> (geprüft: 10 Vorkommen, alle flach), deshalb
    genügt es, zum öffnenden Tag das nächste </div> zu suchen. Ein Zähler wäre hier Theater.
    """
    while (i := rumpf.find('<div class="keep">')) != -1:
        j = rumpf.find("</div>", i)
        if j == -1:
            raise Fehler("div.keep ohne schließendes Tag")
        rumpf = rumpf[:i] + rumpf[i + len('<div class="keep">'):j] + rumpf[j + len("</div>"):]
    return rumpf


def parse(pfad, zielordner, webpfad, nur_struktur=False):
    """Liefert dieselben Felder wie handbuchtext.parse().

    `nur_struktur=True` überspringt das Herauslösen der Bilder und entfernt die Abbildungen
    stattdessen aus dem Rumpf. Das ist für Aufrufer gedacht, die nur Titel und Kapitelanker
    brauchen — das Glossar etwa. Ohne diesen Weg würde jeder Glossarbau 17 Bilder neu nach
    WebP wandeln, für nichts.
    """
    with open(pfad, encoding="utf-8") as f:
        quelle = f.read()
    if "<body" not in quelle:
        raise Fehler(f"{pfad}: kein <body>")
    body = quelle.split("<body", 1)[1].split(">", 1)[1].rsplit("</body>", 1)[0]

    deckblatt = re.search(r'<section class="cover">(.*?)</section>', body, re.S)
    if not deckblatt:
        raise Fehler(f"{pfad}: kein Deckblatt")
    d = deckblatt.group(1)

    def feld(klasse, pflicht=True):
        m = re.search(rf'class="{klasse}">(.*?)</', d, re.S)
        if not m and pflicht:
            raise Fehler(f"{pfad}: Deckblattfeld „{klasse}“ fehlt")
        return _text(m.group(1)) if m else ""

    stand_roh = feld("stand")                      # „Heft 1 · Stand: August 2026“
    teile = [t.strip() for t in stand_roh.split("·")]
    stand = next((t.split(":", 1)[1].strip() for t in teile if t.lower().startswith("stand")), "")
    ausgabe = " · ".join(t for t in teile if not t.lower().startswith("stand"))

    meta = {"titel": feld("title"), "claim": feld("lede"), "stand": stand,
            "ausgabe": ausgabe or feld("rubrik"), "merksatz": "",
            "anreisser": f"<p>{html.escape(feld('intro'))}</p>"}

    # Deckblatt und Inhaltsverzeichnis entfallen: Seitenkopf und Kapitelspalte ersetzen sie.
    rumpf = re.sub(r'<section class="(?:cover|toc)">.*?</section>', "", body, flags=re.S)

    kapitel = []

    def kopf(m):
        nr, titel = m.group("nr"), _text(m.group("titel"))
        kapitel.append((nr, titel))
        return (f'<h2 class="chapter" id="kapitel-{nr}">'
                f'<span class="num">{nr}</span> {m.group("titel").strip()}</h2>')

    rumpf, treffer = re.subn(
        r'<section class="chapter" id="c(?P<nr>\d+)">\s*'
        r'<header class="op">\s*<div class="opnum">\d+</div>\s*'
        r'<h2>(?P<titel>.*?)</h2>\s*</header>', kopf, rumpf, flags=re.S)
    if not treffer:
        raise Fehler(f"{pfad}: keine Kapitel gefunden")

    # Erst die Druckhülle auflösen, dann den Kolophon-Kasten bauen — andersherum fräße das
    # Auflösen dessen schließendes </div>.
    rumpf = _keep_aufloesen(rumpf)

    # Der Kolophon nennt Herausgeber, Bildstand und die Marken von Anthropic. Er gehört auf die
    # Seite, aber nicht in die Kapitelspalte — deshalb ein Kasten am Textende statt eines Kapitels.
    def kolophon(m):
        inhalt = re.sub(r'<h1 class="secttl">(.*?)</h1>', r'<span class="t">\1</span>',
                        m.group(1), flags=re.S)
        return f'<div class="box kolophon">{re.sub(r"<h2>(.*?)</h2>", r"<p><b>\1</b></p>", inhalt, flags=re.S)}</div>'

    rumpf = re.sub(r'<section class="kolophon">(.*?)</section>', kolophon, rumpf, flags=re.S)
    rumpf = re.sub(r"</?section[^>]*>", "", rumpf)     # Kapitel sind jetzt Überschriften
    if nur_struktur:
        rumpf, bilder = re.sub(r"<figure.*?</figure>", "", rumpf, flags=re.S), 0
    else:
        rumpf, bilder = _bilder(rumpf, zielordner, webpfad)

    meta["kapitel"] = kapitel
    meta["abschnitte"] = []          # das Heft hat keine Zwischenüberschriften in den Kapiteln
    meta["bilder"] = bilder
    meta["body"] = rumpf.strip()
    return meta
