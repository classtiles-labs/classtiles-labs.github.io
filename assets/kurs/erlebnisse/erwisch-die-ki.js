// Erlebnis „Erwisch die KI“: ein Elternbrief mit drei eingebauten Fehlern und Ablenkern, die
// verdächtig aussehen, aber stimmen. Antippen löst auf.

export function stellen(daten) {
  return daten.absaetze.flat().filter((t) => typeof t === 'object');
}

export function pruefeTreffer(daten, id) {
  const s = stellen(daten).find((x) => x.id === id);
  return s ? {fehler: s.art === 'fehler', erklaerung: s.erklaerung} : null;
}

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function mount(el, daten) {
  if (!daten?.absaetze) return;
  const gesamt = stellen(daten).filter((s) => s.art === 'fehler').length;
  const gefunden = new Set();
  const absatz = (teile) => teile.map((t) => (typeof t === 'string'
    ? (t === '\n' ? '<br>' : esc(t))
    : `<span role="button" tabindex="0" class="ek-stelle" data-id="${t.id}">${esc(t.text)}</span>`)).join('');
  el.innerHTML = `
    <h2>Erwisch die KI</h2>
    <p class="ek-anleitung">In diesem Brief stecken ${gesamt} Fehler. Tippe auf alles, was dir verdächtig vorkommt.</p>
    <div class="ek-brief"><p class="ek-titel">${esc(daten.titel)}</p>${daten.absaetze.map((a) => `<p>${absatz(a)}</p>`).join('')}</div>
    <p class="ek-meldung" aria-live="polite">Noch nichts angetippt.</p>
    <p class="ek-zaehler">0 von ${gesamt} Fehlern gefunden</p>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>`;
  // Inline-Spans statt Buttons: Sie brechen wie Text um. Tastatur: Enter und Leertaste.
  el.addEventListener('keydown', (ev) => {
    if ((ev.key === 'Enter' || ev.key === ' ') && ev.target.closest('.ek-stelle')) {
      ev.preventDefault();
      ev.target.click();
    }
  });
  el.addEventListener('click', (ev) => {
    const b = ev.target.closest('.ek-stelle');
    if (!b) return;
    const t = pruefeTreffer(daten, b.dataset.id);
    b.classList.add(t.fehler ? 'ek-fehler' : 'ek-ok');
    b.setAttribute('aria-label', `${b.textContent}: ${t.fehler ? 'Fehler' : 'stimmt'}`);
    if (t.fehler) gefunden.add(b.dataset.id);
    el.querySelector('.ek-meldung').innerHTML = `<b>${t.fehler ? 'Erwischt.' : 'Stimmt so.'}</b> ${esc(t.erklaerung)}`;
    el.querySelector('.ek-zaehler').textContent = gefunden.size === gesamt
      ? `${gesamt} von ${gesamt} gefunden. ${daten.aufloesung}`
      : `${gefunden.size} von ${gesamt} Fehlern gefunden`;
  });
}
