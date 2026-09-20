#!/usr/bin/env python3
"""Erzeugt die Vorschaubilder fürs Teilen (Open Graph) — assets/og-classtiles-{de,en}.png.

    python3 tools/pages/og_image.py

Wer einen Link zu classtiles.de in WhatsApp, Instagram, Mastodon oder einen Messenger im
Kollegium stellt, sieht bisher einen nackten Link. Mit diesen Bildern steht dort eine Karte mit
Symbol, Name und Aussage. Das ist kein Rangfaktor bei Google, aber der Weg, auf dem die Seite
realistisch weiterempfohlen wird.

Die Bilder werden erzeugt und mitversioniert; der Lauf ist nur nötig, wenn sich Wortlaut,
Symbol oder der Screenshot ändern. Er braucht die Systemschrift von macOS.

Warum PNG und nicht WebP: Die Vorschau bauen fremde Dienste, nicht ein Browser. Etliche davon
lesen bis heute kein WebP und zeigen dann gar nichts.
"""
import base64
import io
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import shell  # noqa: E402

BREITE, HOEHE = shell.OG_BILD_GROESSE

# Farben aus site.css (:root, helle Fassung) — die Karte soll aussehen wie die Website.
PAPER = (250, 247, 242)
NAVY = (31, 37, 71)
INK_2 = (86, 91, 115)
HAIR = (230, 224, 213)

SF = "/System/Library/Fonts/SFNS.ttf"

TEXTE = {
    "de": dict(titel="ClassTiles",
               zeilen=["Notenverwaltung für Lehrkräfte", "für iPad, iPhone und Mac"],
               fuss="classtiles.de"),
    "en": dict(titel="ClassTiles",
               zeilen=["Grade management for teachers", "for iPad, iPhone and Mac"],
               fuss="classtiles.de"),
}

SCREENSHOT = os.path.join(REPO, "assets", "notentabelle.webp")


def schrift(groesse, schnitt="Regular"):
    if not os.path.exists(SF):
        sys.exit(f"Systemschrift nicht gefunden: {SF} — dieser Lauf braucht macOS.")
    f = ImageFont.truetype(SF, groesse)
    f.set_variation_by_name(schnitt)
    return f


def rundes_rechteck(groesse, radius):
    """Maske mit runden Ecken."""
    maske = Image.new("L", groesse, 0)
    ImageDraw.Draw(maske).rounded_rectangle([0, 0, groesse[0] - 1, groesse[1] - 1],
                                            radius=radius, fill=255)
    return maske


def schatten(karte, box, radius, streuung=26, tiefe=14):
    """Weicher Schlagschatten unter `box` — dieselbe Anmutung wie die Kacheln der Website."""
    ebene = Image.new("RGBA", karte.size, (0, 0, 0, 0))
    ImageDraw.Draw(ebene).rounded_rectangle(
        [box[0], box[1] + tiefe, box[2], box[3] + tiefe], radius=radius, fill=(20, 24, 51, 46))
    karte.alpha_composite(ebene.filter(ImageFilter.GaussianBlur(streuung)))


def app_symbol(kante):
    """Das App-Symbol aus der Data-URI der Shell — dieselbe Quelle wie die Kopfleiste."""
    roh = base64.b64decode(shell.ICON.split(",", 1)[1])
    bild = Image.open(io.BytesIO(roh)).convert("RGBA").resize((kante, kante), Image.LANCZOS)
    bild.putalpha(rundes_rechteck((kante, kante), int(kante * 0.225)))
    return bild


def screenshot(hoehe):
    bild = Image.open(SCREENSHOT).convert("RGBA")
    breite = round(bild.width * hoehe / bild.height)
    return bild.resize((breite, hoehe), Image.LANCZOS)


def karte(lang):
    t = TEXTE[lang]
    bild = Image.new("RGBA", (BREITE, HOEHE), PAPER + (255,))

    # Rechts der Screenshot, angeschnitten — er zeigt, worum es geht, ohne Erklärung.
    shot = screenshot(500)
    x, y = 648, 96
    schatten(bild, (x, y, x + shot.width, y + shot.height), 20)
    shot.putalpha(Image.composite(shot.getchannel("A"),
                                  Image.new("L", shot.size, 0),
                                  rundes_rechteck(shot.size, 20)))
    bild.alpha_composite(shot, (x, y))

    zeichner = ImageDraw.Draw(bild)
    links = 76

    symbol = app_symbol(108)
    bild.alpha_composite(symbol, (links, 104))

    zeichner.text((links, 240), t["titel"], font=schrift(70, "Bold"), fill=NAVY)
    for i, zeile in enumerate(t["zeilen"]):
        zeichner.text((links, 336 + i * 42), zeile, font=schrift(30, "Regular"), fill=INK_2)

    zeichner.line([(links, 466), (links + 56, 466)], fill=HAIR, width=3)
    zeichner.text((links, 486), t["fuss"], font=schrift(26, "Semibold"), fill=NAVY)

    return bild.convert("RGB")


def main():
    for lang in ("de", "en"):
        ziel = os.path.join(REPO, shell.OG_BILD[lang])
        karte(lang).save(ziel, "PNG", optimize=True)
        print(f"{shell.OG_BILD[lang]}  {BREITE}×{HOEHE}  {os.path.getsize(ziel) // 1024} KB")


if __name__ == "__main__":
    main()
