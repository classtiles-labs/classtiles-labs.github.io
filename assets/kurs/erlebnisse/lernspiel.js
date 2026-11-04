// Erlebnis „Lernspiel bauen“: Spiele, die aus einem einzigen Prompt entstanden sind (echte
// Läufe). „Spiel starten“ öffnet das Spiel als eigene Seite — die Website bettet nichts per
// iframe ein. Dazu der Prompt zum Kopieren.
import {kopiere} from '../ticket.js';

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const datum = (iso) => iso.split('-').reverse().join('.');

export function mount(el, daten) {
  if (!daten?.spiele?.length) return;
  el.innerHTML = `
    <h2>Ein Prompt, ein Spiel</h2>
    <p class="ls-anleitung">Jedes dieser Spiele ist aus genau einem Prompt entstanden. Starte eins und spiel zu zweit an einem Tablet oder Rechner.</p>
    <div class="ls-spiele">${daten.spiele.map((s, i) => `
      <article class="ls-spiel">
        <p class="ls-fach">${esc(s.fach)} · ${esc(s.klasse)}</p>
        <h3>${esc(s.titel)}</h3>
        <p class="ls-quelle">${esc(s.modell)}, ${datum(s.datum)}, ein Lauf, ungeändert</p>
        <div class="ls-knoepfe">
          <a class="btn b-solid" href="${esc(s.datei)}">Spiel starten</a>
          <button type="button" class="btn b-line" data-kopiere="${i}">Prompt kopieren</button>
        </div>
        <details><summary>Prompt ansehen</summary><pre class="ls-prompt">${esc(s.prompt)}</pre></details>
        <span class="ticket-meldung" aria-live="polite"></span>
      </article>`).join('')}</div>`;
  el.addEventListener('click', async (ev) => {
    const b = ev.target.closest('[data-kopiere]');
    if (!b) return;
    const karte = b.closest('.ls-spiel');
    const meldung = karte.querySelector('.ticket-meldung');
    if ((await kopiere(daten.spiele[Number(b.dataset.kopiere)].prompt, navigator.clipboard)) === 'kopiert') {
      meldung.textContent = 'Kopiert. In deine KI-App einfügen und die Zeilen unter ANPASSEN ändern.';
    } else {
      karte.querySelector('details').open = true;
      const r = document.createRange();
      r.selectNodeContents(karte.querySelector('.ls-prompt'));
      getSelection().removeAllRanges();
      getSelection().addRange(r);
      meldung.textContent = 'Markiert, jetzt kopieren.';
    }
  });
}
