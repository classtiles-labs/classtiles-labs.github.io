// KI-Kurs: Einstieg auf jeder Kursseite. Liest das Register aus <script id="kurs-netz">,
// führt den Fortschritt (Link-Fragment, auf Wunsch zusätzlich gemerkt), zeichnet auf der
// Übersicht das Liniennetz, lädt die Erlebnisse einer Station und macht Tickets kopierbar.
//
// Ohne dieses Skript bleibt alles lesbar: Die Stationen stehen als Links in der Übersicht, die
// Tickets als Text in der Station.
import {leererStand, besuche, alsFragment, ausFragment, vereinige} from './stand.js';
import {erstelleSpeicher, speicherDesBrowsers} from './speicher.js';
import {netzLayout} from './netz.js';
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
    if (stand.besucht.length || stand.linie) history.replaceState(null, '', alsFragment(stand));
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
    if (knopf.dataset.aktion === 'merken') {
      const ok = speicher.merke(stand);
      zeichneFortschritt();
      if (!ok) meldung('Auf diesem Gerät nicht möglich. Nutze den Link, um weiterzumachen.');
    } else if (knopf.dataset.aktion === 'vergessen') {
      speicher.vergiss();
      zeichneFortschritt();
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
    const antwort = await fetch(new URL(`./daten/${name}.json`, import.meta.url));
    if (antwort.ok) daten = await antwort.json();
    el.classList.add('erlebnis-aktiv');
    modul.mount(el, daten, kontext);
  } catch (fehler) {
    // Ohne Erlebnis bleibt der Ersatztext der Seite stehen.
    console.warn(`KI-Kurs: Erlebnis „${name}“ nicht geladen`, fehler);
  }
}

const esc = (t) => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function zeichneNetz(box, stand) {
  const breite = Math.max(300, Math.min(box.clientWidth || 390, 760));
  const l = netzLayout(netz, {breite});
  const besucht = new Set(stand.besucht);
  const zug = [...stand.besucht].reverse().find((id) => l.stationen.some((s) => s.id === id)) ?? stand.start;
  const teile = [];
  for (const u of l.umstiege) teile.push(`<path class="netz-umstieg" d="${u.pfad}"/>`);
  for (const li of l.linien) {
    teile.push(`<line class="netz-linie linie-${li.id.toLowerCase()}" x1="${li.x1}" y1="${li.y}" x2="${li.x2}" y2="${li.y}"/>`);
  }
  for (const sch of l.schilder) {
    teile.push(`<g class="netz-schild linie-${sch.linie.toLowerCase()}"><rect x="${sch.x}" y="${sch.y - 12}" width="28" height="24" rx="6"/><text x="${sch.x + 14}" y="${sch.y + 5}">${sch.linie}</text></g>`);
  }
  for (const s of l.stationen) {
    const klasse = ['netz-station', `linie-${s.linie.toLowerCase()}`];
    if (s.geplant) klasse.push('geplant');
    if (besucht.has(s.id)) klasse.push('besucht');
    if (s.umstieg) klasse.push('umsteige');
    const form = s.umstieg
      ? `<rect class="${klasse.join(' ')}" x="${s.x - 9}" y="${s.y - 9}" width="18" height="18" rx="9"/>`
      : `<circle class="${klasse.join(' ')}" cx="${s.x}" cy="${s.y}" r="7"/>`;
    teile.push(s.geplant ? form : `<a href="ki-kurs-${s.id}.html" tabindex="-1">${form}</a>`);
  }
  for (const lab of l.labels) {
    const s = l.stationen.find((x) => x.id === lab.id);
    teile.push(`<text class="netz-label${s.geplant ? ' geplant' : ''}" x="${lab.x}" y="${lab.y}" transform="rotate(${lab.winkel} ${lab.x} ${lab.y})">${esc(s.titel)}</text>`);
  }
  const z = l.stationen.find((s) => s.id === zug);
  if (z) {
    teile.push(`<circle class="netz-puls linie-${z.linie.toLowerCase()}" cx="${z.x}" cy="${z.y}" r="9"/>`);
    teile.push(`<g class="netz-zug"><rect x="${z.x - 20}" y="${z.y + 14}" width="40" height="18" rx="9"/><text x="${z.x}" y="${z.y + 27}">Du</text></g>`);
  }
  box.innerHTML = `<svg viewBox="0 0 ${breite} ${l.hoehe}" width="100%" aria-hidden="true" focusable="false">${teile.join('')}</svg>`;
  box.hidden = false;
}

// Erst ganz am Ende starten: Vorher sind die Hilfen weiter unten (esc, zeichneNetz) noch nicht
// initialisiert.
if (netz) start();
