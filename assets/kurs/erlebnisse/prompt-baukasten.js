// Erlebnis „Prompt-Baukasten“: Bausteine wirken kumulativ in fester Reihenfolge. So stammt jede
// gezeigte Antwort aus einem echten Lauf mit genau diesem Prompt (n Bausteine → n+1 Läufe).

// Antippen von Baustein k (0-basiert): ist er an, gehen er und alle danach aus; sonst gehen
// alle bis einschließlich k an. Rückgabe: Anzahl aktiver Bausteine.
export function tippe(stufe, k) {
  return k < stufe ? k : k + 1;
}

export function prompt(daten, stufe) {
  const aktiv = daten.bausteine.slice(0, stufe);
  const vorne = aktiv.filter((b) => b.vorne).map((b) => b.text);
  const hinten = aktiv.filter((b) => !b.vorne).map((b) => b.text);
  return [...vorne, daten.basis, ...hinten].join(' ');
}

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const datum = (iso) => iso.split('-').reverse().join('.');

export function mount(el, daten) {
  if (!daten?.bausteine?.length) return;
  let stufe = 0;
  el.innerHTML = `
    <h2>Prompt-Baukasten</h2>
    <p class="pb-anleitung">Schalte Bausteine dazu und vergleiche die Antworten. Thema: ${esc(daten.thema)}.</p>
    <div class="pb-chips" role="group" aria-label="Bausteine">${daten.bausteine.map((b, i) =>
      `<button type="button" class="pb-chip" data-k="${i}" aria-pressed="false">${esc(b.name)}</button>`).join('')}</div>
    <p class="pb-label">Prompt</p>
    <p class="pb-prompt"></p>
    <p class="pb-label">Antwort <span class="pb-quelle"></span></p>
    <div class="pb-antwort" aria-live="polite"></div>
    <div class="pb-meter" aria-hidden="true"><span></span></div>
    <p class="pb-urteil"></p>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>`;
  function zeichne() {
    el.querySelectorAll('.pb-chip').forEach((c, i) => {
      c.classList.toggle('an', i < stufe);
      c.setAttribute('aria-pressed', String(i < stufe));
    });
    const a = daten.antworten[stufe];
    el.querySelector('.pb-prompt').textContent = prompt(daten, stufe);
    el.querySelector('.pb-antwort').textContent = a.text;
    el.querySelector('.pb-quelle').textContent = `· ${a.modell}, ${datum(a.datum)}, gekürzt`;
    el.querySelector('.pb-meter span').style.width = `${((stufe + 1) / daten.antworten.length) * 100}%`;
    el.querySelector('.pb-urteil').textContent = a.urteil;
  }
  el.addEventListener('click', (ev) => {
    const c = ev.target.closest('.pb-chip');
    if (!c) return;
    stufe = tippe(stufe, Number(c.dataset.k));
    zeichne();
  });
  zeichne();
}
