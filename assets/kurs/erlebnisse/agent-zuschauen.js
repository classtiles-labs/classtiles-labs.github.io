// Erlebnis „Einem Agenten zuschauen“: ein nachgestellter Agent-Ablauf Schritt für Schritt. An
// Freigabe-Schritten hält er an, bis die Lehrkraft „Freigeben“ oder „Stopp“ wählt.

// entscheidungen: Map Schrittindex → 'frei' | 'stopp'
export function naechsterSchritt(ablauf, index, entscheidungen) {
  const s = ablauf.schritte;
  if (s[index]?.freigabe && !entscheidungen.has(index)) return {index, wartetAufFreigabe: true};
  if (index >= s.length - 1) return {index, wartetAufFreigabe: false};
  const n = index + 1;
  return {index: n, wartetAufFreigabe: Boolean(s[n].freigabe && !entscheidungen.has(n))};
}

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const ICON = {plan: '🧭', werkzeug: '🛠', fertig: '✅'};

export function mount(el, daten) {
  if (!daten?.schritte?.length) return;
  let index = 0;
  const entscheidungen = new Map();
  el.innerHTML = `
    <h2>Einem Agenten zuschauen</h2>
    <p class="ag-aufgabe"><span>Aufgabe</span> ${esc(daten.aufgabe)}</p>
    <ol class="ag-schritte" aria-live="polite"></ol>
    <div class="ag-knoepfe"></div>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>`;
  const liste = el.querySelector('.ag-schritte');
  const knoepfe = el.querySelector('.ag-knoepfe');
  // Wartet der Schritt, der gerade angezeigt wird? (naechsterSchritt blickt auf den folgenden.)
  const wartet = () => Boolean(daten.schritte[index].freigabe && !entscheidungen.has(index));
  function zeichne() {
    const wartetAufFreigabe = wartet();
    liste.innerHTML = daten.schritte.slice(0, index + 1).map((s, i) => {
      const e = entscheidungen.get(i);
      const folge = e ? `<p class="ag-folge ag-${e}">${esc(e === 'frei' ? s.beiFreigabe : s.beiStopp)}</p>` : '';
      const wartet = i === index && wartetAufFreigabe ? '<p class="ag-wartet">Der Agent wartet auf deine Freigabe.</p>' : '';
      return `<li class="ag-schritt ag-${s.art}${s.freigabe ? ' ag-freigabe' : ''}">
        <span class="ag-icon" aria-hidden="true">${ICON[s.art] ?? '•'}</span>
        <div><b>${esc(s.titel)}</b>${s.werkzeug ? ` <span class="ag-werkzeug">${esc(s.werkzeug)}</span>` : ''}<p>${esc(s.text)}</p>${wartet}${folge}</div></li>`;
    }).join('');
    const fertig = index >= daten.schritte.length - 1 && !wartetAufFreigabe;
    knoepfe.innerHTML = wartetAufFreigabe
      ? '<button type="button" class="btn b-line" data-aktion="frei">Freigeben</button><button type="button" class="btn b-solid" data-aktion="stopp">Stopp</button>'
      : fertig
        ? '<button type="button" class="btn b-line" data-aktion="neu">Noch einmal</button>'
        : '<button type="button" class="btn b-solid" data-aktion="weiter">Nächster Schritt</button>';
  }
  knoepfe.addEventListener('click', (ev) => {
    const a = ev.target.closest('button[data-aktion]')?.dataset.aktion;
    if (!a) return;
    if (a === 'frei' || a === 'stopp') entscheidungen.set(index, a);
    else if (a === 'weiter') index = naechsterSchritt(daten, index, entscheidungen).index;
    else if (a === 'neu') { index = 0; entscheidungen.clear(); }
    zeichne();
  });
  zeichne();
}
