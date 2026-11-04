// Erlebnis „Die Apps kennenlernen“: echte Screenshots von ChatGPT und Claude mit nummerierten
// Markierungen. Umschalten zwischen den Apps, Bild für Bild weiter.

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export function mount(el, daten) {
  if (!daten?.apps?.length) return;
  let app = 0;
  let bild = 0;
  el.innerHTML = `
    <h2>Zwei Apps, ein Prinzip</h2>
    <p class="ar-anleitung">Wähle eine App und blättere durch die wichtigsten Stellen.</p>
    <div class="ar-schalter" role="group" aria-label="App wählen">${daten.apps.map((a, i) =>
      `<button type="button" data-app="${i}" aria-pressed="false">${esc(a.name)}</button>`).join('')}</div>
    <figure class="ar-figur">
      <div class="ar-bild"></div>
      <figcaption class="ar-titel" aria-live="polite"></figcaption>
    </figure>
    <ol class="ar-legende"></ol>
    <div class="ar-knoepfe">
      <button type="button" class="btn b-line" data-schritt="-1">Zurück</button>
      <span class="ar-zaehler"></span>
      <button type="button" class="btn b-solid" data-schritt="1">Weiter</button>
    </div>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>`;
  function zeichne() {
    const a = daten.apps[app];
    const b = a.bilder[bild];
    el.querySelectorAll('[data-app]').forEach((k) => k.setAttribute('aria-pressed', String(Number(k.dataset.app) === app)));
    el.querySelector('.ar-bild').innerHTML = `<img src="${esc(b.datei)}" alt="${esc(b.alt)}" loading="lazy">` +
      b.markierungen.map((m, i) => `<span class="ar-marke" style="left:${m.x * 100}%;top:${m.y * 100}%" aria-hidden="true">${i + 1}</span>`).join('');
    el.querySelector('.ar-titel').textContent = `${a.name}: ${b.titel} (Stand: ${b.stand})`;
    el.querySelector('.ar-legende').innerHTML = b.markierungen.map((m) => `<li>${esc(m.text)}</li>`).join('');
    el.querySelector('.ar-zaehler').textContent = `Bild ${bild + 1} von ${a.bilder.length}`;
    el.querySelector('[data-schritt="-1"]').disabled = bild === 0;
    el.querySelector('[data-schritt="1"]').disabled = bild === a.bilder.length - 1;
  }
  el.addEventListener('click', (ev) => {
    const k = ev.target.closest('[data-app]');
    if (k) { app = Number(k.dataset.app); bild = 0; zeichne(); return; }
    const s = ev.target.closest('[data-schritt]');
    if (s && !s.disabled) { bild += Number(s.dataset.schritt); zeichne(); }
  });
  zeichne();
}
