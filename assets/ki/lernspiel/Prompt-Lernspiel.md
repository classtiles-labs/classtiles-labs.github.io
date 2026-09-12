Du bist Senior-Frontend-Entwickler und Instructional Designer. Du baust
Unterrichtsspiele, die auf dem Schul-iPad sofort funktionieren.

Baue mir EINE einzige, vollständige HTML-Datei: ein Duell-Lernspiel für zwei
Schüler, die nebeneinander an einem iPad sitzen und gegeneinander antreten.
Links Team A, rechts Team B, geteilter Bildschirm, gemeinsame Uhr.

═══════════════════════════════════════════════════════════════════════
TEIL 1 — HIER ANPASSEN (alles andere unverändert lassen)
═══════════════════════════════════════════════════════════════════════

SCHULFORM:              Gymnasium
JAHRGANG:               8
FACH:                   Englisch
INSTRUKTIONSSPRACHE:    English
  (Sprache aller Knöpfe, Menüs, Rückmeldungen und Überschriften.
   Bei Fremdsprachenunterricht ruhig die Zielsprache, sonst Deutsch.)

SPIELTITEL:             English Hoops
SPORT-METAPHER:         Basketball
  (Was ein Punkt heißt: Korb, Tor, Treffer, Runde, Satz …)
TEAMFARBEN:             Team Blue (türkis) gegen Team Coral (korallrot)

DIE SECHS THEMEN:
  1. Tenses            — Zeiten
  2. If-clauses        — Bedingungssätze Typ 1 und 2
  3. Passive           — Passiv
  4. Relative clauses  — Relativsätze
  5. Vocabulary        — Wortschatz
  6. Mixed grammar     — Modalverben, Steigerung, Adverbien, Gerundium

AUFGABENFORMAT:
  Lückensatz mit ___ an der Lücke, vier Antwortmöglichkeiten,
  davon genau eine richtig. Danach ein Satz Erklärung der Regel.

NIVEAU:
  Allgemeine Wiederholung für den Jahrgang, unabhängig von Lehrwerk
  und Bundesland. Keine Textauszüge aus Schulbüchern.

═══════════════════════════════════════════════════════════════════════
TEIL 2 — FESTE VORGABEN (nicht verändern, nicht weglassen)
═══════════════════════════════════════════════════════════════════════

── A. TECHNIK ──────────────────────────────────────────────────────────

A1  Genau eine .html-Datei. CSS in einem <style> im <head>, JavaScript in
    einem <script> vor </body>. Kein Build, kein Bundler, keine Module.
A2  NULL externe Ressourcen. Keine CDN-Skripte, keine Bibliotheken, kein
    Tailwind, kein React, keine Web-Fonts, keine Bilddateien, keine
    Sounddateien, keine Analytics, keine Tracker, kein Werbecode.
A3  NULL Netzwerkaufrufe. Kein fetch, kein XMLHttpRequest, kein WebSocket.
    Die Datei läuft nach dem Laden vollständig offline.
A4  Schrift ausschließlich per Namen: font-family:Arial,Helvetica,sans-serif.
    Keine @font-face-Regel, keine Schriftdatei.
A5  Alle Grafik per Canvas 2D aus Code gezeichnet. Keine SVG-Dateien, keine
    Emoji als Spielfiguren, keine base64-Bilder.
A6  Favicon als inline data:image/svg+xml im <link rel="icon">, aus
    einfachen Formen zusammengesetzt.
A7  Kein localStorage, kein sessionStorage, keine Cookies, keine Namen,
    keine gespeicherten Ergebnisse. Das Spiel lebt im Speicher der Seite.
A8  Modernes Standard-JavaScript, das Safari auf dem iPad versteht.
    <dialog> mit showModal() für alle Overlays.

── B. INHALT: 72 GEPAARTE AUFGABEN ─────────────────────────────────────

B1  Genau 72 Aufgabenpaare, also 144 verschiedene Sätze.
B2  Genau 12 Paare pro Thema, für alle sechs Themen gleich viele.
B3  Ein Paar besteht aus: Thema, Satz A, Satz B, richtige Antwort, drei
    Ablenker, Erklärung. Datenform als flaches Array:
    ['Thema','Satz A','Satz B','richtig',['falsch1','falsch2','falsch3'],'Erklärung']
B4  Satz A und Satz B üben DIESELBE Regel mit VERSCHIEDENEM Inhalt und
    haben DIESELBE richtige Antwort und DIESELBEN Ablenker. Das ist der
    Kern der Fairness: beide Teams lösen dieselbe Schwierigkeit, aber
    niemand kann beim Nachbarn abschreiben.
    Beispiel: 'We ___ to London last summer.' / 'They ___ to Oxford last
    winter.' → 'went', Ablenker 'have gone','go','are going'.
B5  Alle 144 Sätze sind voneinander verschieden. Keine Dopplung.
B6  Die richtige Antwort darf nicht zusätzlich unter den Ablenkern stehen.
B7  Die Ablenker sind plausibel und typische Schülerfehler, nicht albern.
B8  Die Erklärung ist EIN kurzer Satz und nennt die Regel, nicht nur die
    Lösung. Also 'Abgeschlossene Handlung in der Vergangenheit: simple
    past.' und nicht 'went ist richtig.'
B9  Schreibe alle 72 Paare vollständig aus. Keine Auslassungen, kein
    '// hier weitere ergänzen', kein '...', keine Platzhalter. Wenn die
    Antwortlänge nicht reicht, schreibe direkt weiter, bis die Datei
    komplett ist.

── C. FAIRNESS-MASCHINE ────────────────────────────────────────────────

C1  Gruppiere die Paare nach Thema. Mische innerhalb jedes Themas.
C2  Baue den Stapel in Blöcken von sechs: jeder Block enthält jedes Thema
    genau einmal, die Reihenfolge der Themen wird pro Block neu gemischt.
    So trifft Aufgabe 1 bis 6 alle sechs Themen ab.
C3  Beide Teams bekommen bei gleicher Aufgabennummer dasselbe Paar, also
    dasselbe Thema und dieselbe Regel.
C4  Pro Paar entscheidet ein Zufallswert, welches Team Satz A und welches
    Satz B bekommt. Die Teams bekommen nie denselben Satz.
C5  Die vier Antwortmöglichkeiten werden für jedes Team unabhängig
    gemischt. Gleiche Optionen, andere Reihenfolge.
C6  Jedes Team rückt unabhängig vor. Schnellere Teams sind weiter, sehen
    also zeitgleich ein anderes Thema. Das ist beabsichtigt.
C7  Nach 72 Aufgaben beginnt automatisch ein neu gemischter Durchlauf.
    Das Spiel kann nie leer laufen.
C8  Verwende Fisher-Yates zum Mischen, auf einer Kopie des Arrays.

── D. AUFBAU DES BILDSCHIRMS (von oben nach unten) ─────────────────────

D1  Kopfzeile, dunkel: links Markenzeichen mit rundem Icon und Spieltitel,
    wobei das zweite Wort in der Akzentfarbe steht. Mitte: Fach und
    Jahrgang, klein und grau. Rechts zwei ruhige Knöpfe, Pause und
    Spieldauer.
D2  Anzeigetafel, drei Spalten: links Teamname mit Untertitel und große
    Punktzahl, Mitte die Uhr mit Beschriftung und Statuszeile, rechts
    dasselbe gespiegelt. Punktzahlen sehr groß, fett, mit
    font-variant-numeric:tabular-nums, damit nichts springt.
D3  Zwei Spielfelder nebeneinander, gleich groß, per aspect-ratio, mit
    Eckenrundung oben. In jeder Ecke die Feldbezeichnung in der Teamfarbe.
D4  Dünner Fortschrittsbalken über die ganze Breite, als Farbverlauf von
    der Farbe Team A über Weiß zur Farbe Team B. Er zeigt die restliche
    Zeit, nicht den Punktestand.
D5  Zwei Aufgabenfelder nebeneinander, HELLER Hintergrund als Kontrast zur
    dunklen Halle. Links leicht bläulich, rechts leicht pfirsichfarben.
    Jedes enthält: Themen-Etikett und Aufgabennummer in Großbuchstaben,
    den Satz groß mit farbig hervorgehobener Lücke, vier Antwortknöpfe im
    2x2-Raster mit Buchstabenplakette A B C D, darunter eine Zeile für die
    Rückmeldung mit fester Mindesthöhe, damit das Layout nicht springt.
D6  Fußzeile: links die Grundregel in einem Satz, rechts ein Textknopf,
    der die Anleitung öffnet.
D7  Vier Dialoge: Spieleinstellung, Pause, Ergebnis, Anleitung.

── E. SPIELABLAUF ──────────────────────────────────────────────────────

E1  Beim Laden öffnet sich der Einstellungsdialog automatisch.
E2  Spieldauer wählbar: 1, 2, 3, 5 Minuten oder eigener Wert. Standard ist
    2 Minuten. Der eigene Wert ist eine ganze Zahl von 15 bis 1800
    Sekunden, sonst erscheint eine Fehlermeldung und das Spiel startet
    nicht. Das Zahlenfeld ist gesperrt, solange 'Eigene' nicht gewählt ist.
E3  Nach dem Start ein Countdown von 3, groß und mittig über dem
    abgedunkelten Spiel. Dann läuft die gemeinsame Uhr.
E4  Ein Tipp auf eine Antwort sperrt sofort alle vier Knöpfe dieses Teams
    gegen weitere Eingaben. Ein zweiter Punkt für dieselbe Aufgabe ist
    unmöglich.
E5  Die richtige Antwort wird grün markiert. War die Wahl falsch, wird
    zusätzlich die gewählte Antwort rot markiert.
E6  Richtig bringt genau einen Punkt und einen Korb. Falsch bringt null
    Punkte. Es gibt KEINEN Punktabzug.
E7  Die Rückmeldung zeigt bei richtig 'Richtig! +1' und die Erklärung, bei
    falsch die Lösung und die Erklärung. Sie steht 1600 Millisekunden,
    dann rückt dieses Team automatisch zur nächsten Aufgabe vor.
E8  Zeit messen mit performance.now() und einem Ziel-Zeitstempel, nicht
    mit setInterval-Zählern. Gezeichnet wird in requestAnimationFrame.
E9  Pause hält die Uhr für BEIDE Teams an, auch die laufende
    Rückmeldefrist. Nach dem Fortsetzen bleibt die restliche Frist gleich.
E10 visibilitychange und pagehide pausieren automatisch. Wer die App
    wechselt, verliert keine Zeit.
E11 Eine Antwort nach Ablauf der Zeit zählt nicht und beendet die Runde.
E11a Die Antwortknöpfe sind immer dann gesperrt, wenn nicht gespielt wird,
    also im Einstellungsdialog, im Countdown, in der Pause und nach dem
    Abpfiff. Vorgreifen ist unmöglich.
E11b Die Uhr wechselt in den letzten 10 Sekunden in die Warnfarbe.
E12 Bei Ablauf: Ergebnisdialog mit Sieger oder Unentschieden, je Team die
    Körbe, die Zahl der Antworten und die Trefferquote in Prozent.
E13 Zwei Knöpfe im Ergebnis: Revanche mit gleicher Spieldauer und neu
    gemischtem Stapel, oder Spieldauer ändern.
E14 Escape darf Einstellung und Ergebnis nicht schließen. Bei Pause und
    Anleitung setzt Escape das Spiel fort.
E15 Wer die Anleitung im laufenden Spiel öffnet, pausiert automatisch und
    spielt beim Schließen automatisch weiter.

── F. CANVAS-RENDERER ──────────────────────────────────────────────────

F1  Rechne in einem festen Koordinatensystem von 600 mal 280 und skaliere
    mit ctx.setTransform auf die tatsächliche Canvas-Größe. Dann stimmt
    jede Koordinate auf jedem Display.
F2  Berücksichtige devicePixelRatio, aber deckle ihn bei 2. Setze
    canvas.width nur, wenn sich die Größe wirklich geändert hat.
F3  Szene von hinten nach vorn, alles aus Rechtecken, Ellipsen, Linien und
    Farbverläufen:
    - Hallenhintergrund als senkrechter Verlauf von dunkelblau nach
      graublau
    - Tribüne: drei Reihen aus etwa 22 Zuschauern, versetzt angeordnet,
      jeder ein Ellipsenkopf plus Rechteckkörper, in zwei abwechselnden
      Grautönen, damit die Reihen lebendig wirken
    - Bande als dunkles Band mit einem dünnen Streifen in der Teamfarbe
    - Parkett als warmer Verlauf von braun nach hellbraun, mit
      Dielenlinien in leichter Perspektive und waagerechten Fugen
    - Feldlinien in gebrochenem Weiß: Zone, Freiwurfbogen, Mittelkreis
    - Korbanlage rechts: Ständer, Streben, weißes Brett mit Rahmen und
      orangefarbenem Zielrechteck, Ring als flache Ellipse in Orange,
      Netz aus sechs schrägen plus zwei waagerechten Linien
    - Spielfigur links: Schatten, Beine, Schuhe, Arme, Hose, Trikot in der
      Teamfarbe, Kopf. Gib den beiden Teams verschiedene Hauttöne.
F4  Spiegele die ganze Szene für das rechte Feld mit translate und
    scale(-1,1), damit die Teams einander zugewandt spielen.
F5  Ruhezustand: die Figur wippt sanft mit einem Sinus über die Zeit.
F6  Wurfanimation, ausgelöst durch eine richtige Antwort, etwa 1,3
    Sekunden: die Figur streckt sich, der Ball fliegt auf einer Parabel
    zum Ring, fällt durch und das Netz schwingt kurz nach. Danach ein
    kleiner Funkenkranz in der Teamfarbe rund um den Ring.
F7  Der Ball ist orange mit dunklen Nahtlinien, zwei davon als Bézier-
    Kurven, und dreht sich im Flug.
F8  Zusätzlich erscheint über dem Feld kurz eine Textmarke wie 'SWISH! +1'
    als CSS-Animation, die aufsteigt und ausblendet.
F9  Zeichne gedrosselt auf etwa 30 Bilder je Sekunde. Im Pausenzustand
    zeichne mit dem eingefrorenen Zeitstempel, damit das Bild stillsteht.
F10 Bei prefers-reduced-motion: keine Wippbewegung, kein Ballflug, kein
    Netzschwingen, keine Funken. Die Textmarke bleibt lesbar stehen.

── G. GESTALTUNG ───────────────────────────────────────────────────────

G1  Grundgedanke: dunkle Sporthalle oben, helles Arbeitsblatt unten. Die
    Aufgabe ist immer der hellste Bereich im Bild.
G2  Farben, als CSS-Variablen im :root:
      Hallenblau       #101c2b
      Seitenhintergrund #0a1420
      Team A           #53d6f5
      Team B           #ff947d
      Akzent, Knöpfe   #ff934f bis #fa8748
      Textfarbe dunkel #142537
      Richtig          #08774f
      Falsch           #b43335
G3  Antwortknöpfe mit einem dickeren unteren Rand, der beim Drücken
    schmaler wird. Der Knopf fühlt sich dadurch mechanisch an.
G4  Primärknopf mit einem festen Schatten darunter statt Weichzeichnung.
G5  Große Zahlen mit negativem letter-spacing und Schriftstärke 900.
G6  Etiketten und Beschriftungen klein, in Großbuchstaben, mit weitem
    letter-spacing.
G7  Alle Berührungsflächen mindestens 44 Pixel hoch.
G8  Vier Umbruchpunkte: sehr breit, niedrige Bauhöhe, Tablet hochkant und
    Telefon. Hochkant und schmal wird das Antwortraster einspaltig, die
    Kopfzeile schrumpft, das Seitenverhältnis der Felder wird höher.
    Kein waagerechtes Scrollen, in keiner Breite.
G9  Bei schmalem Bildschirm ein kurzer Hinweis, das Gerät zu drehen.
G10 touch-action:manipulation und -webkit-tap-highlight-color:transparent
    auf allen Knöpfen, damit nichts hakt oder aufblitzt.

── H. BARRIEREFREIHEIT ─────────────────────────────────────────────────

H1  Jeder Abschnitt bekommt ein aria-label. Die Punktzahlen tragen ein
    aria-label, das bei jeder Änderung mitwandert.
H2  Die Rückmeldezeile ist aria-live="polite", der Countdown
    aria-live="assertive", die Fehlermeldung role="alert".
H3  Sichtbarer Fokusrahmen über :focus-visible, mit Abstand zum Element.
H4  Antwortknöpfe tragen aria-label mit dem Antworttext. Die
    Buchstabenplakette ist aria-hidden.
H5  Die Zeitknöpfe sind eine Gruppe mit aria-pressed, kein Radio-Ersatz
    aus Divs.
H6  Kontraste nach WCAG AA, auch für die grünen und roten Zustände.
H7  Die Canvas-Elemente tragen role="img" und ein beschreibendes
    aria-label. Sie sind Schmuck, nie der einzige Informationsträger.

── I. RECHTLICH SAUBER ─────────────────────────────────────────────────

I1  Alles im Spiel ist Eigenentwicklung. Kein Stockmaterial, keine
    Schriftdatei, kein Sound, kein Logo, keine Marke Dritter. Keine
    Vereins-, Liga-, Hersteller- oder Verlagsnamen, auch nicht in
    Beispielsätzen.
I2  Die Aufgaben sind neu geschrieben. Keine Übernahme aus einem Lehrwerk.
I3  Das Spiel erhebt keine Daten. Schreibe das auch sichtbar in die
    Anleitung.
I4  Ergänze im Anleitungsdialog einen kurzen Abschnitt, der offenlegt,
    woher Grafik, Aufgaben und Schrift kommen.

── J. AUSGABEFORMAT ────────────────────────────────────────────────────

J1  Antworte mit dem vollständigen HTML-Code und sonst nichts. Keine
    Einleitung, keine Zusammenfassung danach.
J2  Die Datei beginnt mit <!doctype html> und endet mit </html>.
J3  Keine Codekommentare, die auf fehlende Teile hinweisen. Keine TODOs.
J4  Nenne mir am Ende in einer Zeile den Dateinamen, unter dem ich
    speichern soll.

── K. PRÜFUNG VOR DER ANTWORT ──────────────────────────────────────────

Gehe diese Liste durch, bevor du antwortest. Korrigiere still, was nicht
stimmt, und melde keine Abweichung, sondern liefere es richtig.

K1  Sind es wirklich 72 Paare und 12 pro Thema?
K2  Sind alle 144 Sätze verschieden?
K3  Steht bei keinem Paar die richtige Antwort auch unter den Ablenkern?
K4  Hat jeder Satz eine Lücke oder ist bewusst als Frage formuliert?
K5  Haben Satz A und Satz B jedes Paares dieselbe richtige Antwort?
K6  Existiert jede id, die das Skript anspricht, auch im HTML?
K7  Ist die Datei frei von http- und https-Adressen, abgesehen vom
    SVG-Namensraum im Favicon?
K8  Läuft die Datei ohne Internetverbindung?
K9  Ist der Punktestand gegen Doppelklick und gegen Antworten nach
    Zeitablauf geschützt?
K10 Ist das Skript syntaktisch fehlerfrei und vollständig geschlossen?
