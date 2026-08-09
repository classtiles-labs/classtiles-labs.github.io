#!/usr/bin/env python3
"""Prüft alle internen Links und Anker über alle Seiten der Website.

    python3 tools/check-links.py

Meldet: Ziel existiert nicht · Anker existiert nicht · eingebundene Fremdressource · <form>.
Exit-Code 1, wenn etwas nicht stimmt.

Warum die Fremdressourcen mitgeprüft werden: Die Seite kommt ohne Cookie-Banner aus, weil außer
dem Cookie-freien Cloudflare-Beacon nichts von fremden Servern geladen wird (§ 25 TDDDG). Eine
versehentlich eingebundene Webfont oder ein Embed würde das kippen — und die Aussage in der
Datenschutzerklärung mit.
"""
import os
import re
import sys
from urllib.parse import unquote, urldefrag

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERLAUBT_EXTERN = ("https://static.cloudflareinsights.com/beacon.min.js",)


def pages():
    out = [n for n in sorted(os.listdir(REPO)) if n.endswith(".html")]
    out += ["en/" + n for n in sorted(os.listdir(os.path.join(REPO, "en"))) if n.endswith(".html")]
    return out


def anchors(text):
    return set(re.findall(r'id="([^"]+)"', text))


def main():
    inhalt = {}
    for p in pages():
        with open(os.path.join(REPO, p), encoding="utf-8") as f:
            inhalt[p] = f.read()
    fehler = []

    for seite, text in inhalt.items():
        base = os.path.dirname(seite)

        for url in re.findall(r'(?:src|srcset|href)="([^"]*)"', text):
            if not url or url.startswith(("mailto:", "data:", "http://", "https://")):
                continue
            if url.startswith("#"):
                if url[1:] and url[1:] not in anchors(text):
                    fehler.append(f"{seite}: Anker fehlt → {url}")
                continue
            ziel, frag = urldefrag(unquote(url))
            pfad = (os.path.normpath(os.path.join(REPO, base, ziel)) if ziel
                    else os.path.join(REPO, seite))
            rel = os.path.relpath(pfad, REPO)
            if not os.path.exists(pfad):
                fehler.append(f"{seite}: Ziel fehlt → {url}")
                continue
            if frag and rel in inhalt and frag not in anchors(inhalt[rel]):
                fehler.append(f"{seite}: Anker fehlt → {url}")

        for m in re.finditer(r'<(?:script|link|img|source|iframe)[^>]*(?:src|href)='
                             r'"(https?://[^"]+)"', text):
            if m.group(1) not in ERLAUBT_EXTERN:
                fehler.append(f"{seite}: Fremdressource eingebunden → {m.group(1)}")
        if "<form" in text:
            fehler.append(f"{seite}: enthält ein <form>")

    print(f"{len(inhalt)} Seiten geprüft, {len(fehler)} Beanstandungen")
    for f in fehler:
        print("  " + f)
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
