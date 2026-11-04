// Erlebnis „Feedback geben“: dieselbe Schülerarbeit, zwei echte Antworten. Die erste auf eine
// schlichte Bitte, die zweite mit Kriterien, drei Teilen und du-Ansprache. Ein Check zeigt den Unterschied.
import {kennzahlen} from './differenzieren.js';

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const datum = (iso) => iso.split('-').reverse().join('.');

export function duFormen(text) {
  return (String(text).match(/(?<![\p{L}])(du|dich|dir|dein\p{L}*)(?![\p{L}])/giu) ?? []).length;
}

const FRAGEN = [['wohin', 'Wohin? (Ziel)'], ['stand', 'Wo stehst du? (mit Textstelle)'], ['weiter', 'Wie geht es weiter? (nächster Schritt)']];

export function checkZeilen(l) {
  const du = duFormen(l.text);
  return [
    ['Länge', `${kennzahlen(l.text).woerter} Wörter`, kennzahlen(l.text).woerter <= 200],
    ['Ansprache', du ? `spricht sie mit „du“ an (${du}×)` : 'schreibt über sie, nicht mit ihr', du > 0],
    ['Nächste Schritte', l.schritte === 1 ? '1, konkret' : `${l.schritte} auf einmal`, l.schritte <= 2],
    ...FRAGEN.map(([k, n]) => [n, l.fragen[k] ? 'ja' : 'fehlt', l.fragen[k]]),
  ];
}

function check(l) {
  return checkZeilen(l).map(([n, w, ok]) => `<li class="${ok ? 'ok' : 'nein'}"><span>${esc(n)}</span><b>${esc(w)}</b></li>`).join('');
}

export function mount(el, daten) {
  if (!daten?.laeufe?.length) return;
  let seite = 0;
  el.innerHTML = `
    <h2>Für dich oder für sie?</h2>
    <p class="fc-anleitung">Eine Schülerin aus Klasse 7 hat einen argumentierenden Text geschrieben. Zwei echte Antworten von ${esc(daten.laeufe[0].app)}, dazu ein Feedback-Check.</p>
    <details class="vn-text" open><summary>Schülertext (erfunden)</summary><pre>${esc(daten.schuelertext)}</pre></details>
    <div class="vn-schalter fc-schalter">
      ${daten.laeufe.map((l, i) => `<button type="button" data-i="${i}" aria-pressed="${i === 0}"${i ? ' disabled' : ''}>${esc(l.titel)}</button>`).join('')}
    </div>
    <p class="pb-label">Prompt <span class="pb-quelle"></span></p>
    <pre class="pb-prompt fc-prompt"></pre>
    <div class="fc-raster">
      <div><p class="pb-label">Antwort</p><div class="pb-antwort fc-antwort" aria-live="polite"></div></div>
      <div><p class="pb-label">Feedback-Check</p><ul class="fc-check"></ul></div>
    </div>
    <div class="fc-entscheidung">
      <p><b>${esc(daten.entscheidung.frage)}</b></p>
      <div class="fc-optionen">${daten.entscheidung.optionen.map((o, i) => `<button type="button" class="btn b-line" data-o="${i}">${esc(o.text)}</button>`).join('')}</div>
      <p class="fc-erklaerung" hidden></p>
      <button type="button" class="btn b-solid" data-weiter hidden>Antwort 2 ansehen</button>
    </div>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>`;
  const knoepfe = el.querySelectorAll('[data-i]');
  function zeichne() {
    const l = daten.laeufe[seite];
    knoepfe.forEach((b) => b.setAttribute('aria-pressed', String(Number(b.dataset.i) === seite)));
    el.querySelector('.pb-quelle').textContent = `· ${l.app} ${l.modell}, ${l.modus}, ${datum(l.datum)}`;
    el.querySelector('.fc-prompt').textContent = l.prompt;
    el.querySelector('.fc-antwort').textContent = l.text;
    el.querySelector('.fc-check').innerHTML = check(l);
    el.querySelector('.fc-entscheidung').hidden = seite !== 0;
  }
  el.querySelector('.fc-schalter').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-i]');
    if (!b || b.disabled) return;
    seite = Number(b.dataset.i);
    zeichne();
  });
  el.querySelector('.fc-optionen').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-o]');
    if (!b) return;
    el.querySelectorAll('[data-o]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    const e = el.querySelector('.fc-erklaerung');
    e.textContent = daten.entscheidung.optionen[Number(b.dataset.o)].erklaerung;
    e.hidden = false;
    knoepfe.forEach((k) => { k.disabled = false; });
    const w = el.querySelector('[data-weiter]');
    w.hidden = false;
    w.focus();
  });
  el.querySelector('[data-weiter]').addEventListener('click', () => {
    seite = 1;
    zeichne();
    knoepfe[1].focus();
  });
  zeichne();
}
