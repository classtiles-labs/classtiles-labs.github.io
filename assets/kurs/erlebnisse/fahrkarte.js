// Einstufung „Fahrkarte lösen“: drei Wissensfragen, nach jeder sofort die Auflösung, am Ende
// eine Fahrkarte mit Linie und Einstiegsstation. Keine Punktzahl, jederzeit überspringbar.
import {empfehlung} from '../einstufung.js';

export const WEISS_NICHT = 'weiss-nicht';

// gewaehlt: je Frage der Index der gewählten Antwort oder 'weiss-nicht'
export function auswerten(daten, gewaehlt) {
  const ergebnisse = daten.fragen.map((f, i) => {
    const g = gewaehlt[i];
    if (g === WEISS_NICHT || g === undefined) return WEISS_NICHT;
    return f.antworten[g]?.richtig ? 'richtig' : 'falsch';
  });
  return {ergebnisse, empfehlung: empfehlung(ergebnisse)};
}

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export function mount(el, daten, kontext) {
  if (!daten?.fragen?.length) return;
  const {netz} = kontext;
  const titel = (id) => netz.stationen.find((s) => s.id === id)?.titel ?? id;
  const linienName = (lid) => netz.linien.find((l) => l.id === lid)?.name ?? lid;
  let schritt = -1;
  const gewaehlt = [];

  const fokus = () => el.querySelector('[data-fokus]')?.focus();
  const zeige = (html) => { el.innerHTML = html; fokus(); };

  function start() {
    schritt = -1;
    gewaehlt.length = 0;
    el.innerHTML = `
      <h2>Fahrkarte lösen</h2>
      <p>3 Fragen, 1 Minute: Danach weißt du, auf welcher Linie du einsteigst. Keine Punkte, kein Test.</p>
      <div class="fk-knoepfe">
        <button type="button" class="btn fk-los" data-aktion="los">Fragen starten</button>
        <a class="fk-ueberspringen" href="#liniennetz">Überspringen, ich suche selbst aus</a>
      </div>`;
  }

  function frage() {
    const f = daten.fragen[schritt];
    const antworten = f.antworten.map((a, i) =>
      `<button type="button" class="fk-antwort" data-antwort="${i}">${esc(a.text)}</button>`).join('');
    zeige(`
      <p class="fk-zaehler">Frage ${schritt + 1} von ${daten.fragen.length}</p>
      <h2 tabindex="-1" data-fokus>${esc(f.frage)}</h2>
      <div class="fk-antworten">${antworten}
        <button type="button" class="fk-antwort fk-weissnicht" data-antwort="${WEISS_NICHT}">Weiß ich nicht</button>
      </div>
      <a class="fk-ueberspringen" href="#liniennetz">Überspringen</a>`);
  }

  function aufloesung(wahl) {
    const f = daten.fragen[schritt];
    gewaehlt[schritt] = wahl;
    const richtig = wahl !== WEISS_NICHT && f.antworten[wahl]?.richtig;
    for (const b of el.querySelectorAll('.fk-antwort')) {
      b.disabled = true;
      const i = b.dataset.antwort;
      if (i !== WEISS_NICHT && f.antworten[i]?.richtig) b.classList.add('fk-richtig');
      if (String(wahl) === i && !richtig) b.classList.add('fk-falsch');
    }
    const urteil = wahl === WEISS_NICHT ? 'Kein Problem, so geht es:' : richtig ? 'Richtig.' : 'Nicht ganz.';
    const weiter = schritt < daten.fragen.length - 1 ? 'Nächste Frage' : 'Zur Fahrkarte';
    el.querySelector('.fk-ueberspringen')?.remove();
    el.insertAdjacentHTML('beforeend', `
      <div class="fk-erklaerung" role="status"><b>${urteil}</b> ${esc(f.erklaerung)}</div>
      <button type="button" class="btn fk-los" data-aktion="weiter">${weiter}</button>`);
    el.querySelector('[data-aktion="weiter"]').focus();
  }

  function fahrkarte() {
    const {empfehlung: e} = auswerten(daten, gewaehlt);
    kontext.aendere((s) => ({...s, linie: e.linie, start: e.station}));
    const ziel = `ki-kurs-${e.station}.html`;
    zeige(`
      <p class="fk-zaehler">Deine Fahrkarte</p>
      <h2 tabindex="-1" data-fokus><span class="linie-badge linie-${e.linie.toLowerCase()}">${e.linie}</span> Linie ${e.linie} · ${esc(linienName(e.linie))}</h2>
      <p class="fk-einstieg">Einstieg: <b>${esc(titel(e.station))}</b></p>
      <div class="fk-knoepfe">
        <a class="btn fk-los" href="${ziel}">Einsteigen</a>
        <a class="fk-ueberspringen" href="#liniennetz">Ich steige lieber woanders ein</a>
        <button type="button" class="fk-neu" data-aktion="neu">Noch einmal</button>
      </div>`);
    // Der Einstiegslink trägt den Stand mit; kurs.js schreibt ihn bei jeder Änderung neu.
    kontext.aendere((s) => s);
  }

  el.addEventListener('click', (ev) => {
    // „Überspringen“ scrollt zum Netz, ohne den Anker der Adresse zu ändern (dort steht der Stand).
    const sprung = ev.target.closest('a[href="#liniennetz"]');
    if (sprung) {
      ev.preventDefault();
      const ziel = document.querySelector('.kurs-netz h2') ?? document.getElementById('liniennetz');
      ziel?.setAttribute('tabindex', '-1');
      ziel?.scrollIntoView({block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
      ziel?.focus({preventScroll: true});
      return;
    }
    const b = ev.target.closest('button');
    if (!b) return;
    if (b.dataset.aktion === 'los' || b.dataset.aktion === 'neu') { schritt = 0; gewaehlt.length = 0; frage(); }
    else if (b.dataset.aktion === 'weiter') {
      if (schritt < daten.fragen.length - 1) { schritt++; frage(); } else fahrkarte();
    } else if (b.dataset.antwort !== undefined && !b.disabled) {
      const a = b.dataset.antwort;
      aufloesung(a === WEISS_NICHT ? WEISS_NICHT : Number(a));
    }
  });

  start();
}
