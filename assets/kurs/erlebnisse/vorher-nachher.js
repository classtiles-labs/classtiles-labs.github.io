// Erlebnis „Eigenes Material“: dieselbe Bitte einmal ohne und einmal mit dem eigenen
// Erwartungshorizont als Projektwissen. Beide Antworten stammen aus echten Läufen.

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const datum = (iso) => iso.split('-').reverse().join('.');

export function mount(el, daten) {
  if (!daten?.ohne || !daten?.mit) return;
  let seite = 'ohne';
  el.innerHTML = `
    <h2>Mit und ohne dein Material</h2>
    <p class="vn-anleitung">Dieselbe Bitte, zwei Läufe. Schalte um und vergleiche.</p>
    <div class="vn-schalter" role="tablist">
      <button type="button" role="tab" data-seite="ohne">Ohne Dokument</button>
      <button type="button" role="tab" data-seite="mit">Mit Erwartungshorizont im Projekt</button>
    </div>
    <p class="pb-label">Bitte</p>
    <p class="pb-prompt">${esc(daten.bitte)}</p>
    <details class="vn-text"><summary>Schülertext (erfunden)</summary><pre>${esc(daten.schuelertext)}</pre></details>
    <div class="vn-dokument"><p class="pb-label">Im Projekt hinterlegt</p><p><b>${esc(daten.dokument.titel)}</b></p><pre>${esc(daten.dokument.auszug)}</pre></div>
    <p class="pb-label">Antwort <span class="pb-quelle"></span></p>
    <div class="pb-antwort" aria-live="polite"></div>
    <p class="pb-urteil"></p>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>`;
  function zeichne() {
    const a = daten[seite];
    el.querySelectorAll('[data-seite]').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.seite === seite)));
    el.querySelector('.vn-dokument').hidden = seite !== 'mit';
    el.querySelector('.pb-antwort').textContent = a.text;
    el.querySelector('.pb-quelle').textContent = `· ${a.modell}, ${datum(a.datum)}, gekürzt`;
    el.querySelector('.pb-urteil').textContent = a.urteil;
  }
  el.querySelector('.vn-schalter').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-seite]');
    if (!b) return;
    seite = b.dataset.seite;
    zeichne();
  });
  zeichne();
}
