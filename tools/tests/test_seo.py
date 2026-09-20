"""Tests für die Angaben, die Suchmaschinen lesen: canonical, hreflang, Open Graph,
strukturierte Daten, sitemap.xml, robots.txt.

Aufruf aus dem Repo-Wurzelverzeichnis:  python3 -m unittest discover -s tools/tests -v

Diese Tests prüfen nicht „sieht gut aus", sondern die Regeln, an denen Suchmaschinen eine
Angabe still verwerfen — vor allem die Gegenseitigkeit der Sprachverweise. Ein hreflang, das
nicht zurückzeigt, wird von Google ignoriert; man sieht es der Seite nicht an.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))

import jsonld  # noqa: E402
import shell  # noqa: E402

CANONICAL = re.compile(r'<link rel="canonical" href="([^"]+)">')
ALTERNATE = re.compile(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">')
LDJSON = re.compile(r'<script type="application/ld\+json">\n(.*?)\n  </script>', re.S)
OG = re.compile(r'<meta property="(og:[^"]+)" content="([^"]*)">')
TITLE = re.compile(r'<title>(.*?)</title>', re.S)
DESC = re.compile(r'<meta name="description" content="(.*?)">', re.S)

SITE = "https://classtiles.de"


def pages(root=REPO):
    return shell.pages(root)


def read(name, root=REPO):
    with open(os.path.join(root, name), encoding="utf-8") as f:
        return f.read()


def graph_of(text):
    roh = LDJSON.search(text)
    assert roh, "kein JSON-LD auf der Seite"
    return json.loads(roh.group(1).replace("<\\/", "</"))["@graph"]


def knoten(graph, typ):
    return [n for n in graph if typ in (n["@type"] if isinstance(n["@type"], list)
                                        else [n["@type"]])]


class TestAdressen(unittest.TestCase):
    def test_canonical_of_startseiten_ohne_dateinamen(self):
        self.assertEqual(shell.canonical_of("index.html"), f"{SITE}/")
        self.assertEqual(shell.canonical_of("en/index.html"), f"{SITE}/en/")

    def test_canonical_of_uebrige_seiten(self):
        self.assertEqual(shell.canonical_of("support.html"), f"{SITE}/support.html")
        self.assertEqual(shell.canonical_of("en/privacy.html"), f"{SITE}/en/privacy.html")

    def test_absolute_of_loest_relative_verweise_auf(self):
        self.assertEqual(shell.absolute_of("modul-kalender.html", "index.html#module"),
                         f"{SITE}/#module")
        self.assertEqual(shell.absolute_of("en/module-grades.html", "index.html#module"),
                         f"{SITE}/en/#module")
        self.assertEqual(shell.absolute_of("en/manuals.html", "../handbuecher.html"),
                         f"{SITE}/handbuecher.html")


class TestSprachpaare(unittest.TestCase):
    def test_echte_paare(self):
        for p in ("index.html", "en/index.html", "datenschutz.html", "en/privacy.html",
                  "modul-notenverwaltung.html", "en/module-grades.html",
                  "handbuecher.html", "en/manuals.html"):
            self.assertTrue(shell.is_paired(p), f"{p} sollte ein Sprachpaar sein")

    def test_nur_deutsche_seiten_sind_kein_paar(self):
        """Die Handbücher und der KI-Bereich zeigen auf eine englische Hinweisseite. Das ist ein
        Notausgang für Leser, kein Sprachpaar — als hreflang wäre es falsch."""
        for p in ("handbuch-notenverwaltung.html", "ki-glossar.html", "ki-handbuch-workflows.html",
                  "ki-kurzfassung-ablauf.html", "ki-neues.html"):
            self.assertFalse(shell.is_paired(p), f"{p} ist kein echtes Sprachpaar")

    def test_paarung_ist_symmetrisch(self):
        for p in pages():
            if shell.is_paired(p):
                self.assertTrue(shell.is_paired(shell.twin_page(p)),
                                f"{p} ist gepaart, sein Zwilling aber nicht")


class TestSeitenkopf(unittest.TestCase):
    """Was in den 47 ausgelieferten Seiten wirklich steht."""

    def setUp(self):
        self.inhalt = {p: read(p) for p in pages()}

    def test_jede_seite_hat_genau_einen_canonical_und_er_stimmt(self):
        for p, t in self.inhalt.items():
            treffer = CANONICAL.findall(t)
            self.assertEqual(len(treffer), 1, f"{p}: {len(treffer)} canonical-Angaben")
            self.assertEqual(treffer[0], shell.canonical_of(p), f"{p}: canonical falsch")

    def test_hreflang_nennt_sich_selbst(self):
        """Google wertet eine Sprachgruppe nur aus, wenn jede Seite darin sich selbst nennt."""
        for p, t in self.inhalt.items():
            alternates = dict((code, url) for code, url in ALTERNATE.findall(t))
            if not alternates:
                self.assertFalse(shell.is_paired(p), f"{p} ist gepaart, hat aber kein hreflang")
                continue
            self.assertIn(shell.canonical_of(p), alternates.values(),
                          f"{p}: nennt sich selbst nicht")
            self.assertIn("x-default", alternates, f"{p}: x-default fehlt")

    def test_hreflang_zeigt_zurueck(self):
        """Der Zwilling muss dieselbe Gruppe nennen — sonst verwirft Google beide Seiten.

        Bewusst ohne shell.twin_page: welche Seite hinter einer Adresse steckt, wird aus den
        canonical-Angaben der Dateien selbst erschlossen. Sonst prüfte der Test die Zuordnung
        gegen dieselbe Tabelle, aus der die Seiten erzeugt wurden — und ein Fehler in dieser
        Tabelle bliebe auf beiden Seiten gleich und damit unsichtbar.
        """
        nach_url = {CANONICAL.search(t).group(1): p for p, t in self.inhalt.items()}
        for p, t in self.inhalt.items():
            meine = {(c, u) for c, u in ALTERNATE.findall(t)}
            if not meine:
                continue
            for _, url in meine:
                ziel = nach_url.get(url)
                self.assertIsNotNone(ziel, f"{p}: hreflang auf eine Adresse, die es nicht gibt "
                                           f"→ {url}")
                seine = {(c, u) for c, u in ALTERNATE.findall(self.inhalt[ziel])}
                self.assertEqual(meine, seine,
                                 f"{p} und {ziel} nennen verschiedene Sprachgruppen")

    def test_jede_sprachgruppe_hat_genau_eine_deutsche_und_eine_englische_seite(self):
        """Zwölf deutsche Seiten, die auf dieselbe englische zeigen, wären keine Gruppe: die eine
        englische kann nicht auf zwölf zurückzeigen. Der Fall ist in der Vergangenheit genau so
        entstanden — TWIN schickt jede nur deutsche Seite auf eine Hinweisseite."""
        gruppen = {}
        for p, t in self.inhalt.items():
            eintraege = ALTERNATE.findall(t)
            if eintraege:
                gruppen.setdefault(frozenset(eintraege), []).append(p)
        for gruppe, seiten in gruppen.items():
            self.assertEqual(len(seiten), 2, f"Sprachgruppe mit {len(seiten)} Seiten: {seiten}")
            self.assertEqual(sorted(shell.lang_of(p) for p in seiten), ["de", "en"],
                             f"Sprachgruppe ohne je eine Fassung: {seiten}")
            codes = sorted(c for c, _ in gruppe)
            self.assertEqual(codes, ["de", "en", "x-default"], f"{seiten}: Codes {codes}")

    def test_nur_deutsche_seiten_tragen_kein_hreflang(self):
        for p, t in self.inhalt.items():
            if not shell.is_paired(p):
                self.assertEqual(ALTERNATE.findall(t), [],
                                 f"{p}: hreflang ohne echten Zwilling")

    def test_open_graph_ist_vollstaendig(self):
        pflicht = {"og:type", "og:site_name", "og:locale", "og:title", "og:description",
                   "og:url", "og:image", "og:image:width", "og:image:height", "og:image:alt"}
        for p, t in self.inhalt.items():
            felder = dict(OG.findall(t))
            self.assertTrue(pflicht <= set(felder), f"{p}: fehlt {pflicht - set(felder)}")
            self.assertEqual(felder["og:url"], shell.canonical_of(p), f"{p}: og:url ≠ canonical")
            self.assertTrue(felder["og:image"].startswith(SITE + "/assets/"),
                            f"{p}: Vorschaubild liegt nicht bei uns")

    def test_titel_und_beschreibung_gehoeren_der_seite(self):
        """apply-shell.py darf beides lesen, aber niemals überschreiben."""
        tmp = tempfile.mkdtemp(prefix="seotest-")
        try:
            for name in pages():
                dst = os.path.join(tmp, name)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(os.path.join(REPO, name), dst)
            vorher = {p: (TITLE.search(self.inhalt[p]).group(1),
                          DESC.search(self.inhalt[p]).group(1)) for p in pages()}
            r = subprocess.run([sys.executable, os.path.join(REPO, "tools", "apply-shell.py"),
                                "--root", tmp], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            for p, (titel, desc) in vorher.items():
                t = read(p, tmp)
                self.assertEqual(TITLE.search(t).group(1), titel, f"{p}: Titel verändert")
                self.assertEqual(DESC.search(t).group(1), desc, f"{p}: Beschreibung verändert")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestStrukturierteDaten(unittest.TestCase):
    def setUp(self):
        self.inhalt = {p: read(p) for p in pages()}

    def test_jede_seite_traegt_gueltiges_json_ld(self):
        for p, t in self.inhalt.items():
            graph = graph_of(t)  # wirft, wenn das JSON kaputt ist
            seite = knoten(graph, "WebPage")
            self.assertEqual(len(seite), 1, f"{p}: {len(seite)} WebPage-Knoten")
            self.assertEqual(seite[0]["url"], shell.canonical_of(p), f"{p}: url ≠ canonical")

    def test_json_ld_schliesst_den_kopf_nicht_vorzeitig(self):
        """Ein unmaskiertes </ im JSON würde den Block beenden und den Rest als Text ausgeben."""
        for p, t in self.inhalt.items():
            roh = LDJSON.search(t).group(1)
            self.assertNotIn("</", roh, f"{p}: unmaskiertes </ im JSON-LD")

    def test_keine_erfundenen_bewertungen(self):
        """Sternebewertungen, die es nicht gibt, sind ein Richtlinienverstoß — kein Trick."""
        for p, t in self.inhalt.items():
            self.assertNotIn("aggregateRating", t, f"{p}: erfundene Bewertung")
            self.assertNotIn("reviewCount", t, f"{p}: erfundene Bewertung")

    def test_die_app_steht_nur_auf_den_dafuer_vorgesehenen_seiten(self):
        """Die Startseiten und die Preisseite — sonst keine. Ein SoftwareApplication-Knoten auf
        jeder Seite wäre kein Gewinn, sondern 47-mal dieselbe Behauptung."""
        for p, t in self.inhalt.items():
            hat = bool(knoten(graph_of(t), "SoftwareApplication"))
            self.assertEqual(hat, p in jsonld.APP_SEITEN,
                             f"{p}: SoftwareApplication am falschen Ort")

    def test_der_preis_steht_nur_an_einer_stelle(self):
        """Die Preisseite nennt den Preis im Text, die strukturierten Daten nennen ihn als Zahl.
        Laufen die auseinander, widerspricht sich die Seite selbst — und Google glaubt eher den
        strukturierten Daten als dem Text."""
        deutsch = jsonld.PREIS_VOLLVERSION.replace(".", ",")
        seite = self.inhalt["preise.html"]
        self.assertIn(f"{deutsch}&nbsp;€".replace("&nbsp;", " "),
                      seite.replace("&nbsp;", " ").replace("\u00a0", " "),
                      f"preise.html nennt nicht {deutsch} €")
        app = knoten(graph_of(seite), "SoftwareApplication")[0]
        self.assertEqual(app["offers"]["highPrice"], jsonld.PREIS_VOLLVERSION)
        self.assertEqual(app["offers"]["lowPrice"], "0",
                         "Die kostenlose Fassung gehört in die Preisspanne")

    def test_brotkrumen_nennen_keine_station_zweimal(self):
        """Seiten, die ihren eigenen Reiter hervorheben — Support, Handbücher, Preise, der
        KI-Einstieg — standen sonst zweimal im Pfad: einmal als Bereich, einmal als Seite."""
        for p, t in self.inhalt.items():
            for pfad in knoten(graph_of(t), "BreadcrumbList"):
                eintraege = pfad["itemListElement"]
                namen = [e["name"] for e in eintraege]
                self.assertEqual(len(namen), len(set(namen)), f"{p}: {namen}")
                for e in eintraege[:-1]:
                    self.assertNotEqual(e.get("item"), shell.canonical_of(p),
                                        f"{p}: steht als Zwischenschritt im eigenen Pfad")

    def test_die_fragen_stammen_aus_der_seite(self):
        """Die FAQ-Daten dürfen nicht von der sichtbaren Fassung abweichen — sonst wäre es
        Cloaking. Deshalb werden sie aus dem Markup gelesen, und zwar vollständig."""
        for p in jsonld.FAQ_SEITEN:
            t = self.inhalt[p]
            faq = knoten(graph_of(t), "FAQPage")
            self.assertEqual(len(faq), 1, f"{p}: keine FAQPage")
            self.assertEqual(len(faq[0]["mainEntity"]), t.count("<summary>"),
                             f"{p}: nicht alle Fragen übernommen")
            for frage in faq[0]["mainEntity"]:
                self.assertTrue(frage["name"].strip(), f"{p}: leere Frage")
                self.assertTrue(frage["acceptedAnswer"]["text"].strip(), f"{p}: leere Antwort")
                self.assertNotIn("<", frage["acceptedAnswer"]["text"],
                                 f"{p}: Auszeichnung in der Antwort")

    def test_andere_seiten_bekommen_keine_faq(self):
        """Auch andere Seiten nutzen <details> — für Beiwerk, nicht für Fragen."""
        for p, t in self.inhalt.items():
            if p not in jsonld.FAQ_SEITEN and "<summary>" in t:
                self.assertFalse(knoten(graph_of(t), "FAQPage"), f"{p}: FAQPage zu Unrecht")

    def test_brotkrumen_enden_bei_dieser_seite(self):
        for p, t in self.inhalt.items():
            pfade = knoten(graph_of(t), "BreadcrumbList")
            if p in ("index.html", "en/index.html"):
                self.assertFalse(pfade, f"{p}: Startseite braucht keinen Pfad")
                continue
            self.assertEqual(len(pfade), 1, f"{p}: {len(pfade)} Navigationspfade")
            eintraege = pfade[0]["itemListElement"]
            self.assertNotIn("item", eintraege[-1], f"{p}: letzter Eintrag trägt eine URL")
            self.assertEqual([e["position"] for e in eintraege],
                             list(range(1, len(eintraege) + 1)), f"{p}: Positionen springen")


class TestVorschaubild(unittest.TestCase):
    def test_bilder_liegen_vor_und_haben_die_angesagte_groesse(self):
        from PIL import Image
        for lang, rel in shell.OG_BILD.items():
            pfad = os.path.join(REPO, rel)
            self.assertTrue(os.path.exists(pfad), f"{rel} fehlt — python3 tools/pages/og_image.py")
            with Image.open(pfad) as bild:
                self.assertEqual(bild.size, shell.OG_BILD_GROESSE,
                                 f"{rel}: {bild.size} statt {shell.OG_BILD_GROESSE}")
                self.assertEqual(bild.format, "PNG", f"{rel}: kein PNG")


class TestSitemapUndRobots(unittest.TestCase):
    def test_sitemap_ist_auf_dem_stand(self):
        r = subprocess.run([sys.executable, os.path.join(REPO, "tools", "pages", "sitemap.py"),
                            "--check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_sitemap_nennt_jede_seite_genau_einmal_mit_ihrer_gueltigen_adresse(self):
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9",
              "x": "http://www.w3.org/1999/xhtml"}
        baum = ET.parse(os.path.join(REPO, "sitemap.xml")).getroot()
        locs = [u.find("s:loc", ns).text for u in baum.findall("s:url", ns)]
        self.assertEqual(sorted(locs), sorted(shell.canonical_of(p) for p in pages()))
        self.assertEqual(len(locs), len(set(locs)), "doppelte Adresse in der Sitemap")

    def test_sprachgruppen_in_der_sitemap_decken_sich_mit_dem_seitenkopf(self):
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9",
              "x": "http://www.w3.org/1999/xhtml"}
        baum = ET.parse(os.path.join(REPO, "sitemap.xml")).getroot()
        nach_url = {u.find("s:loc", ns).text: u for u in baum.findall("s:url", ns)}
        for p in pages():
            eintrag = nach_url[shell.canonical_of(p)]
            aus_sitemap = {(l.get("hreflang"), l.get("href"))
                           for l in eintrag.findall("x:link", ns)}
            aus_seite = set(ALTERNATE.findall(read(p)))
            self.assertEqual(aus_sitemap, aus_seite, f"{p}: Sitemap und Seitenkopf weichen ab")

    def test_robots_gibt_die_sitemap_bekannt(self):
        robots = read("robots.txt")
        self.assertIn(f"Sitemap: {SITE}/sitemap.xml", robots)
        self.assertNotIn("Disallow: /\n", robots, "robots.txt sperrt die ganze Seite aus")


class TestBestaetigungsdatei(unittest.TestCase):
    """Googles Bestätigungsdatei liegt in der Wurzel, gehört aber nicht zur Website."""

    def dateien(self):
        return [n for n in sorted(os.listdir(REPO)) if shell.BESTAETIGUNGSDATEI.match(n)]

    def test_muster_trifft_googles_schema_und_sonst_nichts(self):
        self.assertTrue(shell.BESTAETIGUNGSDATEI.match("google8c86af4b4455c27c.html"))
        for kein in ("google-tipps.html", "index.html", "googleXYZ.html", "google.html"):
            self.assertFalse(shell.BESTAETIGUNGSDATEI.match(kein), kein)

    def test_die_datei_bleibt_liegen(self):
        """Google: „Entferne die Datei auch nach bestandener Prüfung nicht." Ist sie weg,
        verliert die Search Console die Bestätigung — und damit alle Daten dort."""
        self.assertTrue(self.dateien(), "Bestätigungsdatei der Search Console fehlt")

    def test_sie_wird_von_allen_werkzeugen_uebergangen(self):
        """Sie hat weder Kopfleiste noch Meta-Block — apply-shell.py würde sonst abbrechen."""
        gepflegt = set(shell.pages(REPO))
        for name in self.dateien():
            self.assertNotIn(name, gepflegt, f"{name} steht in der Seitenliste")
            self.assertNotIn(f"{SITE}/{name}", read("sitemap.xml"), f"{name} steht in der Sitemap")

    def test_ihr_inhalt_ist_die_kennung(self):
        for name in self.dateien():
            self.assertEqual(read(name).strip(), f"google-site-verification: {name}",
                             f"{name}: Inhalt passt nicht zum Dateinamen")


class TestRechnerseite(unittest.TestCase):
    """Der Notenschlüssel-Rechner ist die einzige Seite mit eigenem Skript."""

    SEITE = "notenschluessel-rechner.html"

    # Die Tabellen der App (PointsGradingKey+Defaults.swift). Der Rechner soll nicht anders
    # rechnen als ClassTiles; ändert sich dort etwas, muss dieser Test bewusst mitgeändert
    # werden statt still zu verrutschen.
    CT_1_6 = "[[92,\"1\"],[81,\"2\"],[67,\"3\"],[50,\"4\"],[30,\"5\"],[0,\"6\"]]"

    def setUp(self):
        self.text = read(self.SEITE)

    def test_rechnet_mit_den_tabellen_der_app(self):
        ohne_raum = re.sub(r"\s+", "", self.text)
        self.assertIn(re.sub(r"\s+", "", self.CT_1_6), ohne_raum,
                      "Die 1–6-Tabelle weicht von der App ab")
        for prozent in ("97.3", "94.7", "88.3", "84.7"):   # 1–6 mit Tendenzen
            self.assertIn(prozent, self.text)
        for punkte in ("95", "90", "33", "27", "20"):      # Oberstufe 0–15
            self.assertIn(punkte, self.text)

    def test_kein_formular(self):
        """check-links.py verbietet <form> auf der ganzen Website — ein Formular ginge an einen
        fremden Server. Der Rechner kommt mit Eingabefeldern ohne Formular aus."""
        self.assertNotIn("<form", self.text)


class TestKeinSpeicherAufDemGeraet(unittest.TestCase):
    """§ 25 TDDDG erfasst nicht nur Cookies, sondern jedes Ablegen von Informationen auf dem
    Endgerät. Ein „merke die letzte Einstellung" im Browser-Speicher würde eine Einwilligung
    verlangen — und damit das Banner erzwingen, das diese Website vermeidet. Die Aussage in
    der Datenschutzerklärung hängt daran.

    Gesucht wird nur in <script>-Blöcken, nicht im Fließtext. Die KI-Seiten zeigen Prompts,
    die dem Modell genau das verbieten („Kein localStorage, kein sessionStorage, keine
    Cookies.") — im Text ist das Wort ein Verbot, kein Zugriff.
    """

    SKRIPTE = re.compile(r'<script(?![^>]*application/ld\+json)[^>]*>(.*?)</script>', re.S)
    ZUGRIFF = re.compile(r'\b(?:localStorage|sessionStorage|indexedDB)\s*[.\[]'
                         r'|\bdocument\s*\.\s*cookie')
    HANDLER = re.compile(r'\son[a-z]+\s*=')

    def test_kein_skript_legt_etwas_im_browser_ab(self):
        for p in pages():
            for skript in self.SKRIPTE.findall(read(p)):
                treffer = self.ZUGRIFF.findall(skript)
                self.assertEqual(treffer, [], f"{p} greift auf den Browser-Speicher zu")

    def test_keine_seite_hat_eingebettete_ereignis_handler(self):
        """Ein onclick="…" im Markup wäre ein Skript, das an den <script>-Blöcken vorbeiliefe —
        und damit an der Prüfung darüber."""
        for p in pages():
            ohne_skripte = self.SKRIPTE.sub("", read(p))
            self.assertEqual(self.HANDLER.findall(ohne_skripte), [], f"{p}: Handler im Markup")


class TestShellBloecke(unittest.TestCase):
    def test_der_shell_skriptblock_kommt_genau_einmal_vor(self):
        """apply-shell.py erkennt den Skriptblock an „<script>" plus „(function()". Ein eigenes
        Seitenskript, das genauso anfängt, würde den Ersatz auf sich ziehen und alles bis zum
        Cloudflare-Kommentar verschlucken — Fußzeile inklusive."""
        for p in pages():
            self.assertEqual(read(p).count("<script>\n(function()"), 1,
                             f"{p}: mehrdeutiger Skriptblock")


if __name__ == "__main__":
    unittest.main()
