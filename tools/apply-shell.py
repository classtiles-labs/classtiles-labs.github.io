#!/usr/bin/env python3
"""Schreibt Kopfleiste, Fußzeile, CSS und Skripte aus shell.py in alle Seiten zurück.

    python3 tools/apply-shell.py [--root <verzeichnis>] [--check]

--root   arbeitet auf einer Kopie statt im Repo (für Tests)
--check  ändert nichts, meldet nur, was sich ändern würde (Exit-Code 1, wenn etwas abweicht)

Angefasst werden ausschließlich vier klar abgegrenzte Blöcke. Alles dazwischen — der eigentliche
Seiteninhalt — bleibt unberührt; die Tests prüfen genau das.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell  # noqa: E402

BLOCKS = [
    (re.compile(r'<style>.*?</style>', re.S), lambda p: shell.style_block()),
    (re.compile(r'<div class="bar" id="bar">.*?\n  </div>', re.S), shell.bar_block),
    (re.compile(r'<footer>.*?</footer>', re.S), shell.footer_block),
    (re.compile(r'<script>\n\(function\(\).*?<!-- End Cloudflare Web Analytics -->', re.S),
     lambda p: shell.script_block()),
]


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
            text = pattern.sub(lambda m: build(name).replace("\\", "\\\\"), text, count=1)
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
