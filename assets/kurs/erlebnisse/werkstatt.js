// Erlebnis „Erstes Tool“: eine echte Claude-Code-Sitzung in drei Schritten (Plan, Bau,
// Nachbessern), beide Fassungen des Werkzeugs zum Öffnen und eine Prüfliste fürs eigene Testen.

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const datum = (iso) => iso.split('-').reverse().join('.');

export function fortschritt(abgehakt, gesamt) {
  return abgehakt.size >= gesamt ? `Alle ${gesamt} Punkte geprüft` : `${abgehakt.size} von ${gesamt} geprüft`;
}

export function mount(el, daten) {
  if (!daten?.schritte?.length) return;
  let i = 0;
  const abgehakt = new Set();
  const l = daten.lauf;
  el.innerHTML = `
    <h2>Ein Werkzeug in drei Runden</h2>
    <p class="wk-anleitung">Eine echte Sitzung mit ${esc(l.app)}: ein ${esc(daten.werkzeug)} für den Beamer. Geh die drei Schritte durch und öffne beide Fassungen.</p>
    <div class="wk-schritte">${daten.schritte.map((s, n) => `<button type="button" data-n="${n}" aria-pressed="${n === 0}">${esc(s.titel)}</button>`).join('')}</div>
    <p class="pb-label">Du schreibst</p>
    <pre class="pb-prompt wk-prompt"></pre>
    <p class="pb-label">${esc(l.app)} antwortet <span class="pb-quelle"></span></p>
    <div class="pb-antwort wk-antwort" aria-live="polite"></div>
    <div class="wk-kommentar"></div>
    <a class="btn b-solid wk-oeffnen" hidden></a>
    <div class="wk-pruefen">
      <p><b>Deine Prüfliste beim Testen</b> <span class="wk-stand">${fortschritt(abgehakt, daten.pruefliste.length)}</span></p>
      <div class="wk-liste">${daten.pruefliste.map((p, n) => `<button type="button" class="wk-punkt" data-p="${n}" aria-pressed="false">${esc(p)}</button>`).join('')}</div>
    </div>
    <p class="ew-hinweis">${esc(l.app)} ${esc(l.version)}, ${esc(l.modell)}, ${esc(l.modus)}, ${datum(l.datum)}. ${esc(daten.hinweis)}</p>`;
  const knoepfe = el.querySelectorAll('[data-n]');
  function zeichne() {
    const s = daten.schritte[i];
    knoepfe.forEach((b) => b.setAttribute('aria-pressed', String(Number(b.dataset.n) === i)));
    el.querySelector('.wk-prompt').textContent = s.prompt;
    el.querySelector('.wk-antwort').textContent = s.antwort;
    el.querySelector('.pb-quelle').textContent = `· nach ${s.sekunden} Sekunden`;
    el.querySelector('.wk-kommentar').textContent = s.kommentar;
    const a = el.querySelector('.wk-oeffnen');
    a.hidden = !s.datei;
    if (s.datei) { a.href = s.datei; a.textContent = s.oeffnen; }
  }
  el.querySelector('.wk-schritte').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-n]');
    if (!b) return;
    i = Number(b.dataset.n);
    zeichne();
  });
  el.querySelector('.wk-liste').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-p]');
    if (!b) return;
    const n = Number(b.dataset.p);
    if (abgehakt.has(n)) abgehakt.delete(n); else abgehakt.add(n);
    b.setAttribute('aria-pressed', String(abgehakt.has(n)));
    el.querySelector('.wk-stand').textContent = fortschritt(abgehakt, daten.pruefliste.length);
  });
  zeichne();
}
