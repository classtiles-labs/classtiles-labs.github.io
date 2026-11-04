// Erlebnis „Das Gedächtnis der KI“: Ein Chat wächst, bis die ersten Nachrichten aus dem
// Kontextfenster fallen. Vereinfacht mit kleinen Zahlen; das Prinzip ist das echte.

// Index der ältesten Nachricht, die noch ins Fenster passt (von der neuesten aus gezählt).
export function sichtbar(nachrichten, fenster) {
  let summe = 0;
  for (let i = nachrichten.length - 1; i >= 0; i--) {
    summe += nachrichten[i].tokens;
    if (summe > fenster) return i + 1;
  }
  return 0;
}

export function belegt(nachrichten, ab) {
  return nachrichten.slice(ab).reduce((s, m) => s + m.tokens, 0);
}

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function mount(el, daten) {
  if (!daten?.nachrichten?.length) return;
  let anzahl = 2;
  el.innerHTML = `
    <h2>Das Gedächtnis der KI</h2>
    <p class="kf-anleitung">Ein Chat zur Planung eines Wandertags. Tippe auf „Weiter“ und beobachte die Anzeige oben.</p>
    <div class="kf-zaehler"><span class="kf-text"></span><span class="kf-spur"><span></span></span></div>
    <ol class="kf-chat" aria-live="polite"></ol>
    <div class="kf-knoepfe">
      <button type="button" class="btn b-solid" data-aktion="weiter">Weiter</button>
      <button type="button" class="btn b-line" data-aktion="neu" hidden>Noch einmal</button>
    </div>
    <div class="kf-aha" hidden><b>${esc(daten.aha)}</b></div>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>`;

  const chat = el.querySelector('.kf-chat');
  function zeichne() {
    const sicht = daten.nachrichten.slice(0, anzahl);
    const ab = sichtbar(sicht, daten.fenster);
    const voll = belegt(sicht, ab);
    el.querySelector('.kf-text').textContent = `Kontext: ${voll} von ${daten.fenster} Token`;
    el.querySelector('.kf-spur span').style.width = `${Math.min(100, (voll / daten.fenster) * 100)}%`;
    chat.innerHTML = sicht.map((m, i) => {
      const raus = i < ab;
      const klassen = ['kf-nachricht', `kf-${m.wer}`, raus ? 'kf-raus' : '', m.vergessen ? 'kf-vergessen' : ''].join(' ');
      return `<li class="${klassen}"><span class="kf-wer">${m.wer === 'du' ? 'Du' : 'KI'}</span>${esc(m.text)}${raus ? '<span class="kf-marke">nicht mehr im Kontext</span>' : ''}</li>`;
    }).join('');
    const fertig = anzahl >= daten.nachrichten.length;
    el.querySelector('[data-aktion="weiter"]').hidden = fertig;
    el.querySelector('[data-aktion="neu"]').hidden = !fertig;
    el.querySelector('.kf-aha').hidden = !fertig;
    chat.lastElementChild?.scrollIntoView({block: 'nearest', behavior: 'smooth'});
  }
  el.addEventListener('click', (ev) => {
    const b = ev.target.closest('button[data-aktion]');
    if (!b) return;
    anzahl = b.dataset.aktion === 'weiter' ? anzahl + 1 : 2;
    zeichne();
  });
  zeichne();
}
