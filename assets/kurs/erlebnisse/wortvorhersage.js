// Erlebnis „Sei die KI“: Wort für Wort wählen wie ein Sprachmodell, mit einem Regler für die
// Temperatur. Wahlweise wählt man selbst oder lässt „die KI“ nach der Verteilung ziehen.

// Wahrscheinlichkeiten in Prozent → Verteilung bei Temperatur T (p^(1/T), normiert).
export function verteilung(prozente, temperatur) {
  const w = prozente.map((p) => Math.pow(Math.max(p, 0) / 100, 1 / temperatur));
  const s = w.reduce((a, b) => a + b, 0);
  return w.map((x) => x / s);
}

// zufall in [0, 1): Index der gezogenen Möglichkeit.
export function ziehe(vert, zufall) {
  let summe = 0;
  for (let i = 0; i < vert.length; i++) {
    summe += vert[i];
    if (zufall < summe) return i;
  }
  return vert.length - 1;
}

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const prozent = (x) => (x < 0.01 ? (x * 100).toLocaleString('de-DE', {maximumFractionDigits: 1}) : Math.round(x * 100)) + ' %';

export function mount(el, daten) {
  if (!daten?.stufen?.length) return;
  let stufe = 0;
  let temperatur = daten.regler.start;
  const gewaehlt = [];

  el.innerHTML = `
    <h2>Sei die KI</h2>
    <p class="ew-anleitung">Tippe auf das Wort, das du als Nächstes schreiben würdest. Oder lass die KI ziehen.</p>
    <p class="ew-satz" aria-live="polite"></p>
    <div class="ew-balken"></div>
    <div class="ew-knoepfe">
      <button type="button" class="btn b-line" data-aktion="ziehen">Die KI wählen lassen</button>
      <button type="button" class="btn b-line" data-aktion="neu" hidden>Noch einmal</button>
    </div>
    <label class="ew-regler">Vorsichtig
      <input type="range" min="${daten.regler.min}" max="${daten.regler.max}" step="0.1" value="${temperatur}" aria-label="Temperatur: vorsichtig bis kreativ">
      Kreativ</label>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>
    <div class="ew-aha" hidden><b>${esc(daten.aha)}</b> Probier es noch einmal ganz rechts am Regler: Dann kommen auch Wörter dran, die fast nie passen.</div>`;

  const satz = el.querySelector('.ew-satz');
  const balken = el.querySelector('.ew-balken');
  const regler = el.querySelector('input[type=range]');

  function zeichne() {
    satz.innerHTML = `${esc(daten.satz)} ${gewaehlt.map((w) => `<mark>${esc(w)}</mark>`).join(' ')}`;
    const s = daten.stufen[stufe];
    if (!s) {
      balken.innerHTML = '';
      el.querySelector('[data-aktion="ziehen"]').hidden = true;
      el.querySelector('[data-aktion="neu"]').hidden = false;
      el.querySelector('.ew-aha').hidden = false;
      return;
    }
    const v = verteilung(s.optionen.map(([, p]) => p), temperatur);
    balken.innerHTML = s.optionen.map(([wort], i) => `
      <button type="button" class="ew-option" data-i="${i}">
        <span class="ew-wort">${esc(wort)}</span>
        <span class="ew-spur"><span style="width:${(v[i] * 100).toFixed(1)}%"></span></span>
        <span class="ew-prozent">${prozent(v[i])}</span>
      </button>`).join('');
  }

  function nimm(i) {
    gewaehlt.push(daten.stufen[stufe].optionen[i][0]);
    stufe++;
    zeichne();
  }

  el.addEventListener('click', (ev) => {
    const opt = ev.target.closest('.ew-option');
    if (opt) return nimm(Number(opt.dataset.i));
    const b = ev.target.closest('button[data-aktion]');
    if (!b) return;
    if (b.dataset.aktion === 'ziehen' && daten.stufen[stufe]) {
      const v = verteilung(daten.stufen[stufe].optionen.map(([, p]) => p), temperatur);
      nimm(ziehe(v, Math.random()));
    } else if (b.dataset.aktion === 'neu') {
      stufe = 0;
      gewaehlt.length = 0;
      el.querySelector('[data-aktion="ziehen"]').hidden = false;
      b.hidden = true;
      el.querySelector('.ew-aha').hidden = true;
      zeichne();
    }
  });
  regler.addEventListener('input', () => { temperatur = Number(regler.value); zeichne(); });
  zeichne();
}
