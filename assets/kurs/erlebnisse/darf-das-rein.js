// Erlebnis „Darf das in die KI?“: Karten mit „Geht klar“ oder „Lieber nicht“, nach jeder die
// Begründung. Keine Punktzahl im Vordergrund, sondern die Faustregel am Ende.

export function bewerte(karte, antwort) {
  return {richtig: antwort === karte.ok, warum: karte.warum};
}

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function mount(el, daten) {
  if (!daten?.karten?.length) return;
  let i = 0;
  let richtig = 0;
  el.innerHTML = `
    <h2>Darf das in die KI?</h2>
    <p class="dd-anleitung">Du willst eine KI-App nutzen. Was davon darf hinein?</p>
    <p class="dd-zaehler"></p>
    <div class="dd-karte" aria-live="polite"></div>
    <div class="dd-knoepfe">
      <button type="button" class="btn dd-nein" data-antwort="nein">Lieber nicht</button>
      <button type="button" class="btn dd-ja" data-antwort="ja">Geht klar</button>
    </div>
    <p class="dd-warum" aria-live="polite"></p>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>`;
  const karte = el.querySelector('.dd-karte');
  function zeige() {
    const fertig = i >= daten.karten.length;
    el.querySelector('.dd-zaehler').textContent = fertig ? 'Fertig' : `Karte ${i + 1} von ${daten.karten.length}`;
    karte.classList.remove('weg-links', 'weg-rechts');
    karte.innerHTML = fertig
      ? `<b>${richtig} von ${daten.karten.length} wie empfohlen.</b> ${esc(daten.aufloesung)}`
      : esc(daten.karten[i].text);
    el.querySelector('.dd-knoepfe').hidden = fertig;
  }
  el.addEventListener('click', (ev) => {
    const b = ev.target.closest('button[data-antwort]');
    if (!b || i >= daten.karten.length) return;
    const ja = b.dataset.antwort === 'ja';
    const r = bewerte(daten.karten[i], ja);
    if (r.richtig) richtig++;
    const k = daten.karten[i];
    el.querySelector('.dd-warum').innerHTML = `<b>${k.ok ? 'Geht klar.' : 'Lieber nicht.'}</b> ${esc(r.warum)}`;
    karte.classList.add(ja ? 'weg-rechts' : 'weg-links');
    i++;
    setTimeout(zeige, matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 220);
  });
  zeige();
}
