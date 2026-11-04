// KI-Kurs: Einstieg auf jeder Kursseite. Liest das Register aus <script id="kurs-netz">,
// führt den Fortschritt (Link-Fragment, auf Wunsch zusätzlich gemerkt), zeichnet auf der
// Übersicht das Liniennetz, lädt die Erlebnisse einer Station und macht Tickets kopierbar.
//
// Ohne dieses Skript bleibt alles lesbar: Die Stationen stehen als Links in der Übersicht, die
// Tickets als Text in der Station.
import {leererStand, besuche, alsFragment, ausFragment, vereinige, ersetzbarerHash} from './stand.js';
import {erstelleSpeicher, speicherDesBrowsers} from './speicher.js';
import {netzSvg} from './netz.js';
import {kopiere} from './ticket.js';

const netzEl = document.getElementById('kurs-netz');
const netz = netzEl ? JSON.parse(netzEl.textContent) : null;


function start() {
  const IDS = netz.stationen.map((s) => s.id);
  const speicher = erstelleSpeicher(speicherDesBrowsers());
  let stand = vereinige(ausFragment(location.hash, IDS), speicher.lade(IDS)) ?? leererStand();

  const stationEl = document.querySelector('main.station[data-station]');
  if (stationEl) stand = besuche(stand, stationEl.dataset.station);

  const beobachter = [];
  const kontext = {
    netz,
    stand: () => stand,
    aendere(f) {
      stand = f(stand);
      nachAenderung();
    },
    beobachte(f) {
      beobachter.push(f);
    },
  };

  function nachAenderung() {
    speicher.aktualisiere(stand);
    if ((stand.besucht.length || stand.linie) && ersetzbarerHash(location.hash)) history.replaceState(null, '', alsFragment(stand));
    verlinke();
    zeichneFortschritt();
    for (const f of beobachter) f(stand);
  }

  // Kurslinks tragen den Stand weiter, damit er ohne Speicher von Seite zu Seite reist.
  function verlinke() {
    for (const a of document.querySelectorAll('a[href^="ki-kurs"]')) {
      const [basis, hash = ''] = a.getAttribute('href').split('#');
      if (hash && !hash.startsWith('stand=')) continue;
      a.setAttribute('href', stand.besucht.length || stand.linie ? basis + alsFragment(stand) : basis);
    }
  }

  // ---- Fortschritt ----
  const box = document.getElementById('kurs-fortschritt');
  const gebaut = netz.stationen.filter((s) => s.status === 'gebaut').map((s) => s.id);

  function zeichneFortschritt() {
    if (!box) return;
    const n = stand.besucht.filter((id) => gebaut.includes(id)).length;
    const gemerkt = speicher.istGemerkt();
    box.className = 'fortschritt-box';
    box.innerHTML = `
      <p class="fortschritt-zeile"><b>Dein Fortschritt:</b> ${n} von ${gebaut.length} Stationen besucht${gemerkt ? ' · auf diesem Gerät gemerkt' : ''}</p>
      <div class="fortschritt-knoepfe">
        ${gemerkt
          ? '<button type="button" class="btn b-line" data-aktion="vergessen">Vergessen</button>'
          : '<button type="button" class="btn b-solid" data-aktion="merken">Fortschritt auf diesem Gerät merken</button>'}
        <button type="button" class="btn b-line" data-aktion="link">Fortschritt als Link kopieren</button>
      </div>
      <p class="fortschritt-hinweis">Gespeichert wird nur, welche Stationen du besucht hast, und nur in diesem Browser.${gemerkt ? ' „Vergessen“ löscht es wieder.' : ' Ohne Antippen speichert die Seite nichts.'}</p>
      <p class="fortschritt-meldung" aria-live="polite"></p>`;
  }

  box?.addEventListener('click', async (ev) => {
    const knopf = ev.target.closest('button[data-aktion]');
    if (!knopf) return;
    const meldung = (t) => { box.querySelector('.fortschritt-meldung').textContent = t; };
    // Nach dem Neuzeichnen bekommt der Ersatzknopf den Fokus, sonst landet die Tastatur oben.
    const fokus = (aktion) => box.querySelector(`[data-aktion="${aktion}"]`)?.focus();
    if (knopf.dataset.aktion === 'merken') {
      const ok = speicher.merke(stand);
      zeichneFortschritt();
      fokus(ok ? 'vergessen' : 'link');
      if (!ok) meldung('Auf diesem Gerät nicht möglich. Nutze den Link, um weiterzumachen.');
    } else if (knopf.dataset.aktion === 'vergessen') {
      speicher.vergiss();
      zeichneFortschritt();
      fokus('merken');
      meldung('Vergessen. Auf diesem Gerät ist nichts mehr gespeichert.');
    } else if (knopf.dataset.aktion === 'link') {
      const url = location.origin + location.pathname + alsFragment(stand);
      if ((await kopiere(url, navigator.clipboard)) === 'kopiert') {
        meldung('Link kopiert. Öffne ihn auf einem anderen Gerät, dann geht es dort weiter.');
      } else {
        const feld = document.createElement('input');
        feld.className = 'fortschritt-linkfeld';
        feld.readOnly = true;
        feld.value = url;
        feld.setAttribute('aria-label', 'Link zu deinem Fortschritt');
        box.querySelector('.fortschritt-linkfeld')?.remove();
        box.append(feld);
        feld.select();
        meldung('Markiert, jetzt kopieren.');
      }
    }
  });

  // ---- Tickets ----
  for (const pre of document.querySelectorAll('.ticket-prompt')) {
    const knopf = document.createElement('button');
    knopf.type = 'button';
    knopf.className = 'btn b-solid ticket-knopf';
    knopf.textContent = 'Prompt kopieren';
    const meldung = document.createElement('span');
    meldung.className = 'ticket-meldung';
    meldung.setAttribute('aria-live', 'polite');
    pre.after(knopf, meldung);
    knopf.addEventListener('click', async () => {
      if ((await kopiere(pre.textContent, navigator.clipboard)) === 'kopiert') {
        meldung.textContent = 'Kopiert. Jetzt in deine KI-App einfügen.';
      } else {
        const r = document.createRange();
        r.selectNodeContents(pre);
        const sel = getSelection();
        sel.removeAllRanges();
        sel.addRange(r);
        meldung.textContent = 'Markiert, jetzt kopieren.';
      }
    });
  }

  // ---- Liniennetz (Übersicht) ----
  const netzBox = document.getElementById('liniennetz');
  if (netzBox) {
    const zeichne = () => zeichneNetz(netzBox, stand);
    zeichne();
    beobachter.push(zeichne);
    let warte;
    addEventListener('resize', () => { clearTimeout(warte); warte = setTimeout(zeichne, 150); });
  }

  // ---- Erlebnisse ----
  for (const el of document.querySelectorAll('[data-erlebnis]')) mountErlebnis(el.dataset.erlebnis, el, kontext);

  nachAenderung();
}

export async function mountErlebnis(name, el, kontext) {
  if (!/^[a-z0-9-]+$/.test(name)) return;
  try {
    const modul = await import(`./erlebnisse/${name}.js`);
    let daten = null;
    // Ein Erlebnis ohne Daten erklärt das mit „export const DATEN = false“ — dann kein Abruf.
    if (modul.DATEN !== false) {
      const antwort = await fetch(new URL(`./daten/${name}.json`, import.meta.url));
      if (antwort.ok) daten = await antwort.json();
    }
    el.classList.add('erlebnis-aktiv');
    modul.mount(el, daten, kontext);
  } catch (fehler) {
    // Ohne Erlebnis bleibt der Ersatztext der Seite stehen.
    console.warn(`KI-Kurs: Erlebnis „${name}“ nicht geladen`, fehler);
  }
}

function zeichneNetz(box, stand) {
  const breite = Math.max(300, Math.min(box.clientWidth || 390, 760));
  const fragment = stand.besucht.length || stand.linie ? alsFragment(stand) : '';
  box.innerHTML = netzSvg(netz, stand, fragment, breite);
  box.hidden = false;
}

// Erst ganz am Ende starten: Vorher sind die Hilfen weiter unten (esc, zeichneNetz) noch nicht
// initialisiert.
if (netz) start();
