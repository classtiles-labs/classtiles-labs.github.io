#!/usr/bin/env python3
"""Schreibt Kopfleiste, Fußzeile, CSS und Skripte aus shell.py in alle Seiten zurück.

    python3 tools/apply-shell.py [--root <verzeichnis>] [--check]

--root   arbeitet auf einer Kopie statt im Repo (für Tests)
--check  ändert nichts, meldet nur, was sich ändern würde (Exit-Code 1, wenn etwas abweicht)

Angefasst werden ausschließlich fünf klar abgegrenzte Blöcke. Alles dazwischen — der eigentliche
Seiteninhalt — bleibt unberührt; die Tests prüfen genau das.

Der Meta-Block (canonical, hreflang, Open Graph, strukturierte Daten, Seitensymbol) reicht vom
ersten <link> im Kopf bis zum Symbol. Titel und Beschreibung werden **nicht** überschrieben: sie
gehören zur Seite, nicht zur Shell — der Block liest sie nur, um sie an Open Graph und die
strukturierten Daten weiterzureichen.
"""
import argparse
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell  # noqa: E402

TITLE = re.compile(r'<title>(.*?)</title>', re.S)
DESC = re.compile(r'<meta name="description" content="(.*?)">', re.S)

# Der Meta-Block beginnt beim ersten <link rel="canonical"> bzw. <link rel="alternate"> — die
# Alternative fängt die Seiten ab, die noch die alte Fassung tragen — und endet beim Symbol.
META = re.compile(r'<link rel="(?:canonical|alternate)"[^>]*>.*?<link rel="icon"[^>]*>', re.S)

BLOCKS = [
    (META, lambda p, t: shell.meta_block(p, _titel(p, t), _beschreibung(p, t), t)),
    (re.compile(r'<style>.*?</style>', re.S), lambda p, t: shell.style_block()),
    (re.compile(r'<div class="bar" id="bar">.*?\n  </div>', re.S), lambda p, t: shell.bar_block(p)),
    (re.compile(r'<footer>.*?</footer>', re.S), lambda p, t: shell.footer_block(p)),
    (re.compile(r'<script>\n\(function\(\).*?<!-- End Cloudflare Web Analytics -->', re.S),
     lambda p, t: shell.script_block()),
]


def _feld(regex, was, path, text):
    m = regex.search(text)
    if not m:
        sys.exit(f"{path}: {was} fehlt — ohne sie lassen sich Open Graph und die strukturierten "
                 f"Daten nicht aufbauen")
    wert = m.group(1).strip()
    if not wert:
        sys.exit(f"{path}: {was} ist leer")
    return wert


def _titel(path, text):
    return _feld(TITLE, "<title>", path, text)


def _beschreibung(path, text):
    wert = _feld(DESC, 'meta name="description"', path, text)
    # Eine Beschreibung jenseits von ~160 Zeichen schneidet Google ab; ein Hinweis genügt, der
    # Lauf bricht deswegen nicht ab.
    if len(html.unescape(wert)) > 200:
        print(f"  Hinweis: {path}: description ist {len(html.unescape(wert))} Zeichen lang")
    return wert


def pages(root):
    out = [n for n in sorted(os.listdir(root)) if n.endswith(".html")]
    endir = os.path.join(root, "en")
    if os.path.isdir(endir):
        out += ["en/" + n for n in sorted(os.listdir(endir)) if n.endswith(".html")]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    changed = []
    for name in pages(a.root):
        path = os.path.join(a.root, name)
        text = original = open(path, encoding="utf-8").read()
        for pattern, build in BLOCKS:
            if not pattern.search(text):
                sys.exit(f"{name}: Block {pattern.pattern[:30]}… nicht gefunden")
            # Ersatz als Funktion: re.sub deutet in deren Rückgabewert keine \1-/\g-Sequenzen
            # aus — der Block geht unverändert in die Seite, Backslashes inklusive.
            # `quelle` ist die Fassung vor diesem Ersatz — der Meta-Block liest daraus Titel,
            # Beschreibung und die Fragen der Support-Seite.
            quelle = text
            text = pattern.sub(lambda m: build(name, quelle), text, count=1)
        if text != original:
            changed.append(name)
            if not a.check:
                open(path, "w", encoding="utf-8").write(text)

    verb = "würden sich ändern" if a.check else "geändert"
    print(f"{len(pages(a.root))} Seiten geprüft, {len(changed)} {verb}")
    for name in changed:
        print("  " + name)
    if a.check and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
