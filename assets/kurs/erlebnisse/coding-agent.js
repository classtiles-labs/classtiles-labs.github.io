// Erlebnis „Claude Code & Codex“: ein nachgestellter Zeitraffer, wie aus einem Satz ein fertiges
// Werkzeug wird, und eine knappe Gegenüberstellung der beiden Coding-Agenten.

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const uhr = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
const MARKE = {du: 'Du', agent: 'Agent', befehl: '$', datei: '✎', frage: '?', fertig: '✓'};

export function mount(el, daten) {
  if (!daten?.schritte?.length) return;
  let n = 0;
  let timer = null;
  const ruhig = matchMedia('(prefers-reduced-motion: reduce)').matches;
  el.innerHTML = `
    <h2>Vom Satz zum Werkzeug</h2>
    <div class="tm-fenster ca-fenster">
      <div class="tm-leiste" aria-hidden="true"><i></i><i></i><i></i><span>Coding-Agent im Ordner „notenschluessel“</span><b class="ca-uhr">0:00</b></div>
      <ol class="ca-log" aria-live="polite"></ol>
    </div>
    <div class="ca-knoepfe">
      <button type="button" class="btn b-solid" data-aktion="abspielen">Abspielen</button>
      <button type="button" class="btn b-line" data-aktion="schritt">Einzelschritt</button>
    </div>
    <p class="ca-ergebnis" hidden>${esc(daten.ergebnis.text)} <a href="${esc(daten.ergebnis.datei)}">Rechner öffnen</a></p>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>
    <table class="ca-vergleich">
      <caption>Claude Code und Codex im Vergleich (Stand: November 2026)</caption>
      <thead><tr><th scope="col"></th>${daten.vergleich.spalten.map((s) => `<th scope="col">${esc(s)}</th>`).join('')}</tr></thead>
      <tbody>${daten.vergleich.zeilen.map((z) => `<tr><th scope="row">${esc(z.merkmal)}</th>${z.werte.map((w) => `<td>${esc(w)}</td>`).join('')}</tr>`).join('')}</tbody>
    </table>`;
  const log = el.querySelector('.ca-log');
  function zeichne() {
    log.innerHTML = daten.schritte.slice(0, n).map((s) =>
      `<li class="ca-${s.art}"><span class="ca-marke">${MARKE[s.art]}</span><span>${esc(s.text)}</span></li>`).join('');
    el.querySelector('.ca-uhr').textContent = uhr(n ? daten.schritte[n - 1].zeit : 0);
    const fertig = n >= daten.schritte.length;
    el.querySelector('.ca-ergebnis').hidden = !fertig;
    el.querySelector('[data-aktion="abspielen"]').textContent = fertig ? 'Noch einmal' : timer ? 'Anhalten' : 'Abspielen';
    el.querySelector('[data-aktion="schritt"]').hidden = fertig;
    log.lastElementChild?.scrollIntoView({block: 'nearest'});
  }
  function weiter() {
    if (n < daten.schritte.length) n++;
    if (n >= daten.schritte.length) { clearInterval(timer); timer = null; }
    zeichne();
  }
  el.addEventListener('click', (ev) => {
    const a = ev.target.closest('[data-aktion]')?.dataset.aktion;
    if (a === 'schritt') { clearInterval(timer); timer = null; weiter(); }
    if (a === 'abspielen') {
      if (n >= daten.schritte.length) { n = 0; zeichne(); }
      if (timer) { clearInterval(timer); timer = null; zeichne(); return; }
      timer = setInterval(weiter, ruhig ? 400 : 900);
      weiter();
    }
  });
  zeichne();
}
