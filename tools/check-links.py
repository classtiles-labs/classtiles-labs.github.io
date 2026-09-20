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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell  # noqa: E402
from urllib.parse import unquote, urldefrag

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERLAUBT_EXTERN = ("https://static.cloudflareinsights.com/beacon.min.js",)

SITE = "https://classtiles.de/"

# <link rel="canonical"> und <link rel="alternate" hreflang="…"> sind Angaben *über* die Seite,
# keine eingebundene Ressource: der Browser lädt daraus nichts, es entsteht kein Zugriff auf einen
# fremden Server. Sie dürfen deshalb eine absolute Adresse tragen — aber nur unsere eigene. Ein
# canonical auf eine fremde Domain wäre kein Datenschutzproblem, sondern ein schwerer SEO-Fehler:
# er verschenkt die Seite an den dort Genannten.
META_LINK = re.compile(r'rel="(?:canonical|alternate)"')

# Dasselbe für die absoluten Adressen in den Open-Graph-Angaben.
META_URL = re.compile(r'<meta [^>]*(?:property|name)="(og:(?:image|url)|twitter:image)"[^>]*'
                      r'content="(https?://[^"]+)"')


def anchors(text):
    return set(re.findall(r'id="([^"]+)"', text))


def main():
    inhalt = {}
    for p in shell.pages(REPO):
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

        for m in re.finditer(r'<(script|link|img|source|iframe)([^>]*?)(?:src|href)='
                             r'"(https?://[^"]+)"', text):
            tag, attribute, url = m.groups()
            if url in ERLAUBT_EXTERN:
                continue
            if tag == "link" and META_LINK.search(attribute):
                if not url.startswith(SITE):
                    fehler.append(f"{seite}: canonical/alternate zeigt nach außen → {url}")
                continue
            fehler.append(f"{seite}: Fremdressource eingebunden → {url}")

        for m in META_URL.finditer(text):
            if not m.group(2).startswith(SITE):
                fehler.append(f"{seite}: {m.group(1)} zeigt nach außen → {m.group(2)}")
        if "<form" in text:
            fehler.append(f"{seite}: enthält ein <form>")

    print(f"{len(inhalt)} Seiten geprüft, {len(fehler)} Beanstandungen")
    for f in fehler:
        print("  " + f)
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
