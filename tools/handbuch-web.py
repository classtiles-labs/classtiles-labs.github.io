#!/usr/bin/env python3
"""Übersetzt ein Druck-Handbuch aus ~/mobai in eine Seite der Website.

    python3 tools/handbuch-web.py ~/mobai/handbuch --slug notenverwaltung --modul 1 [--pdf]

Die Quelle bleibt unverändert. Deckblatt und Inhaltsverzeichnis sind Druck-Logik und entfallen;
den Rest der Auszeichnung übernimmt das Skript unverändert — die Klassennamen der Quelle
(.figtitle, .sehen, .tun, .box, .ui) werden vom Handbuch-CSS unter `.hb` gestylt. Dadurch
funktioniert der Konverter auch für die kommenden Handbücher, ohne dass er ihren Inhalt kennt.

Die PNG-Screenshots werden nach WebP gewandelt (rund ein Fünftel der Größe, gleiche Optik).
Mit --pdf wird zusätzlich das PDF aus denselben WebP-Dateien neu gebaut (rund 3 statt 14 MB);
dafür werden Google Chrome und ~/mobai/build-handbuch.py gebraucht.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell  # noqa: E402

# Modulnummer → (Farb-Token, Glyphen-Name, Modulseite, Modulname)
MODULE_META = {
    1: ("m1", "grades", "modul-notenverwaltung.html", "Notenverwaltung"),
    2: ("m2", "calendar", "modul-kalender.html", "Kalender"),
    3: ("m3", "planning", "modul-planung.html", "Planung"),
    4: ("m4", "groups", "modul-gruppen.html", "Gruppen & Sitzordnung"),
    5: ("m5", "documentation", "modul-dokumentation.html", "Dokumentation"),
    6: ("m6", "tasks", "modul-klassengeschaefte.html", "Klassengeschäfte"),
}


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).replace("&shy;", "").replace("\xad", "").strip()


def parse(folder):
    """Liest handbuch.html und liefert Metadaten plus das Inhaltsfragment."""
    with open(os.path.join(folder, "handbuch.html"), encoding="utf-8") as f:
        src = f.read()
    body = src.split("<body>", 1)[1].rsplit("</body>", 1)[0]

    cover = re.search(r'<section class="cover">.*?</section>', body, re.S).group(0)
    meta = {
        "titel": strip_tags(re.search(r"<h1>(.*?)</h1>", cover, re.S).group(1)),
        "claim": strip_tags(re.search(r'<p class="claim">(.*?)</p>', cover, re.S).group(1)),
        "modul": int(re.search(r"Modul (\d+) von", cover).group(1)),
    }
    kolophon = dict(re.findall(r'<span class="k">(.*?)</span><span class="v">(.*?)</span>', cover))
    meta["app"] = kolophon.get("App-Version", "")
    meta["stand"] = kolophon.get("Stand", "")
    meta["abbildungshinweis"] = kolophon.get("Abbildungen", "")
    meta["beispielklasse"] = kolophon.get("Beispielklasse", "")

    # Deckblatt und Inhaltsverzeichnis raus — beides wird durch Seitenkopf und Kapitelliste ersetzt.
    body = re.sub(r'<section class="cover">.*?</section>', "", body, flags=re.S)
    body = re.sub(r'<section class="toc">.*?</section>', "", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)

    kapitel = []

    def anchor(m):
        num = int(strip_tags(m.group(1)))
        titel = strip_tags(m.group(2))
        kapitel.append((num, titel))
        return (f'<h2 class="chapter" id="kapitel-{num}">'
                f'<span class="num">{num}</span>{m.group(2)}</h2>')

    body = re.sub(r'<h2 class="chapter"><span class="num">(.*?)</span>(.*?)</h2>', anchor, body,
                  flags=re.S)

    meta["kapitel"] = kapitel
    meta["abbildungen"] = body.count("<figure")
    meta["body"] = body.strip()
    return meta


def png_size(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                         capture_output=True, text=True, check=True).stdout
    w = int(re.search(r"pixelWidth: (\d+)", out).group(1))
    h = int(re.search(r"pixelHeight: (\d+)", out).group(1))
    return w, h


def convert_images(body, folder, slug, root, max_px=1800):
    """PNG → WebP, `img src` umbiegen, Maße und lazy-loading setzen."""
    outdir = os.path.join(root, "assets", "handbuch", slug)
    os.makedirs(outdir, exist_ok=True)
    used = set()

    def one(m):
        tag, rel = m.group(0), m.group(1)
        name = os.path.basename(rel)
        used.add(name)
        src = os.path.join(folder, rel)
        dst = os.path.join(outdir, os.path.splitext(name)[0] + ".webp")
        with tempfile.TemporaryDirectory() as tmp:
            scaled = os.path.join(tmp, "s.png")
            shutil.copyfile(src, scaled)
            w, h = png_size(scaled)
            if max(w, h) > max_px:
                # sips -Z setzt die längere Kante immer exakt auf den Wert — auch nach oben.
                # Nur skalieren, wenn das Original größer ist, sonst würden kleine Bilder
                # (z. B. das winzige Testbild) unnötig aufgeblasen.
                subprocess.run(["sips", "-Z", str(max_px), scaled, "--out", scaled],
                               check=True, capture_output=True)
                w, h = png_size(scaled)
            subprocess.run(["cwebp", "-q", "82", "-alpha_q", "90", "-m", "6", "-quiet",
                            scaled, "-o", dst], check=True)
        webrel = f"assets/handbuch/{slug}/{os.path.basename(dst)}"
        tag = tag.replace(f'src="{rel}"', f'src="{webrel}" width="{w}" height="{h}" loading="lazy"')
        return tag

    body = re.sub(r'<img[^>]*src="(screenshots/[^"]+)"[^>]*>', one, body)

    vorhanden = {n for n in os.listdir(os.path.join(folder, "screenshots"))
                 if n.lower().endswith(".png")}
    for name in sorted(vorhanden - used):
        print(f"  übersprungen (nicht referenziert): screenshots/{name}")
    return body


def rebuild_pdf(folder, slug, root, dst):
    """Das PDF aus den WebP-Bildern neu rendern — rund ein Fünftel der Größe, gleiche Optik.

    Benutzt den vorhandenen Renderer ~/mobai/build-handbuch.py; er erwartet neben sich ein
    Verzeichnis mit handbuch.html und screenshots/. Deshalb wird beides in einem temporären
    Verzeichnis nachgebaut — die Quelle in ~/mobai bleibt unangetastet.
    """
    builder = os.path.expanduser("~/mobai/build-handbuch.py")
    if not os.path.exists(builder):
        print("  --pdf übersprungen: ~/mobai/build-handbuch.py nicht gefunden")
        return False
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, "handbuch")
        with open(os.path.join(folder, "handbuch.html"), encoding="utf-8") as f:
            src = f.read()
        src = re.sub(r'src="screenshots/([^"]+)\.png"', r'src="screenshots/\1.webp"', src)
        shutil.copytree(os.path.join(root, "assets", "handbuch", slug),
                        os.path.join(work, "screenshots"))
        open(os.path.join(work, "handbuch.html"), "w", encoding="utf-8").write(src)
        shutil.copyfile(builder, os.path.join(tmp, "build-handbuch.py"))
        r = subprocess.run([sys.executable, os.path.join(tmp, "build-handbuch.py"),
                            "handbuch", os.path.basename(dst)], capture_output=True, text=True)
        if r.returncode != 0:
            print("  --pdf fehlgeschlagen, Original-PDF bleibt liegen:")
            print("   ", (r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout)
                  else "keine Meldung")
            return False
        shutil.copyfile(os.path.join(work, os.path.basename(dst)), dst)
    return True


def build_page(meta, slug, pdf_name):
    farbe, ikone, modulseite, modulname = MODULE_META[meta["modul"]]

    nav = "".join(f'<li><a href="#kapitel-{n}">{html.escape(t)}</a></li>'
                  for n, t in meta["kapitel"])
    toc = (f'<details class="hbtoc"><summary>Inhalt · {len(meta["kapitel"])} Kapitel</summary>'
           f'<div class="answer"><ol>{nav}</ol></div></details>')

    zeilen = [f'<span><b>Stand</b> {html.escape(meta["stand"])}</span>',
              f'<span><b>App-Version</b> {html.escape(meta["app"])}</span>',
              f'<span><b>Abbildungen</b> {html.escape(meta["abbildungshinweis"])}</span>',
              f'<span><b>Beispielklasse</b> {html.escape(meta["beispielklasse"])}</span>']

    body = f'''    <a class="back" href="handbuecher.html">← Alle Handbücher</a>
    <div class="hbhead" style="--c:var(--{farbe})">
      <span class="glyph">{shell.GLYPHS[ikone]}</span>
      <div>
        <div class="eyebrow">Benutzerhandbuch · Modul {meta["modul"]} von 6</div>
        <h1>{html.escape(meta["titel"])}</h1>
        <p class="claim">{html.escape(meta["claim"])}</p>
      </div>
    </div>
    <div class="hbmeta">{"".join(zeilen)}</div>
    <div class="cta" style="margin-top:20px">
      <a class="btn b-line" href="assets/handbuch/{pdf_name}" download>PDF laden</a>
    </div>
    {toc}

    <div class="hblayout" style="--c:var(--{farbe})">
      <nav class="hbnav" aria-label="Kapitel">
        <h4>Kapitel</h4>
        <ol>{nav}</ol>
      </nav>
      <article class="hb">
{meta["body"]}
        <div class="hbfoot">
          <a href="handbuecher.html">← Alle Handbücher</a>
          <a href="{modulseite}">{html.escape(modulname)} im Überblick →</a>
        </div>
      </article>
    </div>
'''
    titel = f'Handbuch {meta["titel"]} — ClassTiles'
    desc = (f'Benutzerhandbuch zum ClassTiles-Modul {meta["titel"]}: {meta["claim"]}. '
            f'{len(meta["kapitel"])} Kapitel mit {meta["abbildungen"]} Abbildungen, '
            f'online lesbar und als PDF.')
    return shell.page(f"handbuch-{slug}.html", titel, desc, body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--modul", type=int, required=True, choices=range(1, 7))
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    a = ap.parse_args()

    folder = os.path.abspath(os.path.expanduser(a.folder))
    meta = parse(folder)
    if meta["modul"] != a.modul:
        sys.exit(f"--modul {a.modul}, aber das Deckblatt sagt Modul {meta['modul']}")

    meta["body"] = convert_images(meta["body"], folder, a.slug, a.root)

    pdfs = [n for n in sorted(os.listdir(folder)) if n.lower().endswith(".pdf")]
    if len(pdfs) != 1:
        sys.exit(f"Genau ein PDF erwartet, gefunden: {pdfs}")
    pdf_name = pdfs[0]
    os.makedirs(os.path.join(a.root, "assets", "handbuch"), exist_ok=True)
    ziel_pdf = os.path.join(a.root, "assets", "handbuch", pdf_name)
    shutil.copyfile(os.path.join(folder, pdf_name), ziel_pdf)
    if a.pdf:
        rebuild_pdf(folder, a.slug, a.root, ziel_pdf)

    page = build_page(meta, a.slug, pdf_name)
    out = os.path.join(a.root, f"handbuch-{a.slug}.html")
    open(out, "w", encoding="utf-8").write(page)

    mb = os.path.getsize(ziel_pdf) / 1048576
    print(f'{a.slug}: {len(meta["kapitel"])} Kapitel, {meta["abbildungen"]} Abbildungen, '
          f'Stand {meta["stand"]}, App {meta["app"]}, PDF {mb:.1f} MB')
    print(f"  → {os.path.relpath(out, a.root)}")


if __name__ == "__main__":
    main()
