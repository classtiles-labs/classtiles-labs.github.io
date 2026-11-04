// Erlebnis „Superpowers“: ein Vorhaben Phase für Phase (Beispiel, nachgestellt), jeweils mit der
// Frage, was ohne diese Phase passiert.

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function naechste(i, n) {
  return Math.min(i + 1, n - 1);
}

export function mount(el, daten) {
  if (!daten?.phasen?.length) return;
  let i = 0;
  const n = daten.phasen.length;
  el.innerHTML = `
    <h2>Ein Vorhaben in fünf Phasen</h2>
    <p class="sp-anleitung">Das Beispiel: ein ${esc(daten.beispiel)}. Geh die fünf Phasen durch und tipp auf „Und ohne?“, um zu sehen, was die Phase verhindert.</p>
    <div class="sp-phasen">${daten.phasen.map((p, k) => `<button type="button" data-k="${k}" aria-pressed="${k === 0}" aria-label="Phase ${k + 1}: ${esc(p.titel)}"><span>${k + 1}</span><em>${esc(p.titel)}</em></button>`).join('')}</div>
    <div class="sp-karte" aria-live="polite">
      <p class="sp-titel"></p>
      <p class="sp-skills"></p>
      <p class="sp-so"></p>
      <button type="button" class="btn b-line" data-ohne aria-expanded="false">Und ohne diese Phase?</button>
      <p class="sp-ohne" hidden></p>
    </div>
    <button type="button" class="btn b-solid" data-weiter>Nächste Phase</button>
    <div class="sp-bilanz" hidden>
      <p><b>${esc(daten.bilanz.titel)}</b></p>
      <ul>${daten.bilanz.zeilen.map((z) => `<li>${esc(z)}</li>`).join('')}</ul>
    </div>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>`;
  const knoepfe = el.querySelectorAll('[data-k]');
  const ohne = el.querySelector('[data-ohne]');
  function zeichne() {
    const p = daten.phasen[i];
    knoepfe.forEach((b) => b.setAttribute('aria-pressed', String(Number(b.dataset.k) === i)));
    el.querySelector('.sp-titel').textContent = `Phase ${i + 1} · ${p.titel}`;
    el.querySelector('.sp-skills').innerHTML = p.skills.map((s) => `<code>${esc(s)}</code>`).join(' ');
    el.querySelector('.sp-so').textContent = p.so;
    const o = el.querySelector('.sp-ohne');
    o.textContent = p.ohne;
    o.hidden = true;
    ohne.setAttribute('aria-expanded', 'false');
    el.querySelector('[data-weiter]').hidden = i === n - 1;
    if (i === n - 1) el.querySelector('.sp-bilanz').hidden = false;
  }
  el.querySelector('.sp-phasen').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-k]');
    if (!b) return;
    i = Number(b.dataset.k);
    zeichne();
  });
  ohne.addEventListener('click', () => {
    const o = el.querySelector('.sp-ohne');
    o.hidden = !o.hidden;
    ohne.setAttribute('aria-expanded', String(!o.hidden));
  });
  el.querySelector('[data-weiter]').addEventListener('click', () => {
    i = naechste(i, n);
    zeichne();
    (i === n - 1 ? knoepfe[i] : el.querySelector('[data-weiter]')).focus();
  });
  zeichne();
}
