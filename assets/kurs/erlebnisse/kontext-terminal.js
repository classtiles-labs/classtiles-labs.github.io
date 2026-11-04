// Erlebnis „Kontext und Befehle“: eine nachgebaute Sitzung in Claude Code oder Codex. Arbeit füllt
// den Kontext, Slash-Befehle zeigen, fassen zusammen oder fangen neu an. Nichts davon ist echte KI.

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function startzustand(werkzeug) {
  return {werkzeug, gespraech: 0, schritt: 0, frueher: [], themen: [], benutzt: []};
}

const summe = (o) => Object.values(o).reduce((a, b) => a + b, 0);

export function belegt(z, daten) {
  return Math.min(100, summe(daten.werkzeuge[z.werkzeug].grundlast) + z.gespraech);
}

function balken(prozent, breite = 12) {
  const voll = Math.round((prozent / 100) * breite);
  return '█'.repeat(voll) + '░'.repeat(breite - voll);
}

export function anzeigeText(z, daten) {
  const p = belegt(z, daten);
  return daten.werkzeuge[z.werkzeug].anzeigeText.replace('{p}', p).replace('{f}', 100 - p);
}

export function kontextZeilen(z, daten) {
  const w = daten.werkzeuge[z.werkzeug];
  const teile = [...Object.entries(w.grundlast), [daten.texte.gespraech, z.gespraech]];
  teile.push([daten.texte.frei, 100 - belegt(z, daten)]);
  const breite = Math.max(...teile.map(([name]) => name.length)) + 1;
  return teile.map(([name, p]) => `${name.padEnd(breite)}${balken(p)} ${String(p).padStart(3)} %`);
}

function arbeite(eingabe, z, daten) {
  const w = daten.werkzeuge[z.werkzeug];
  const schritt = daten.arbeit[z.schritt % daten.arbeit.length];
  const neu = {...z, gespraech: z.gespraech + schritt.prozent, schritt: z.schritt + 1,
    themen: z.themen.length ? z.themen : [schritt.thema]};
  const ausgabe = [`● ${schritt.antwort}`];
  if (belegt(neu, daten) >= w.autoCompact) {
    neu.gespraech = daten.zusammenfassung;
    ausgabe.push(w.texte.autoCompact);
  } else if (belegt(neu, daten) >= daten.warnung) {
    ausgabe.push(w.texte.warnung.replace('{p}', belegt(neu, daten)));
  }
  return {ausgabe, zustand: neu, eingabe};
}

export function fuehreAus(eingabe, z, daten) {
  const text = eingabe.trim();
  if (!text) return {ausgabe: [], zustand: z};
  if (!text.startsWith('/')) return arbeite(text, z, daten);
  const w = daten.werkzeuge[z.werkzeug];
  const [befehl, ...rest] = text.split(/\s+/);
  const arg = rest.join(' ');
  const b = w.befehle[w.alias?.[befehl] ?? befehl];
  const zz = {...z, benutzt: z.benutzt.includes(b?.art) ? z.benutzt : [...z.benutzt, b?.art].filter(Boolean)};
  if (!b) {
    if (w.fehlt[befehl]) return {ausgabe: [w.fehlt[befehl]], zustand: z};
    return {ausgabe: [daten.texte.unbekannt.replace('{b}', befehl)], zustand: z};
  }
  switch (b.art) {
    case 'kontext':
      return {ausgabe: [b.titel, ...kontextZeilen(zz, daten)], zustand: zz};
    case 'compact': {
      if (zz.gespraech <= daten.zusammenfassung) return {ausgabe: [b.leer], zustand: z};
      const vorher = belegt(zz, daten);
      const neu = {...zz, gespraech: daten.zusammenfassung};
      const zeilen = [b.fertig.replace('{vorher}', vorher).replace('{nachher}', belegt(neu, daten))];
      if (arg) zeilen.push(b.mitAnweisung ? b.mitAnweisung.replace('{a}', arg) : b.ohneAnweisung);
      return {ausgabe: zeilen, zustand: neu};
    }
    case 'neu': {
      const frueher = w.resumeNachNeu && zz.gespraech > 0 && zz.themen.length ? [zz.themen[0], ...zz.frueher] : zz.frueher;
      return {ausgabe: [b.fertig], zustand: {...zz, gespraech: 0, themen: [], frueher}, leeren: Boolean(b.leertFenster)};
    }
    case 'status':
      return {ausgabe: b.zeilen.map((l) => l.replace('{belegt}', belegt(zz, daten)).replace('{frei}', 100 - belegt(zz, daten))), zustand: zz};
    case 'resume': {
      const liste = [...zz.frueher, ...daten.sitzungen];
      return {ausgabe: [b.titel, ...liste.map((s, i) => `  ${i + 1}. ${s}`), b.hinweis], zustand: zz};
    }
    case 'hilfe':
      return {ausgabe: Object.entries(w.befehle).map(([n, x]) => `${n.padEnd(12)} ${x.kurz}`), zustand: zz};
    default:
      return {ausgabe: b.zeilen, zustand: zz};
  }
}

export function mount(el, daten) {
  if (!daten?.werkzeuge) return;
  let wahl = Object.keys(daten.werkzeuge)[0];
  let z = startzustand(wahl);
  const verlauf = [];
  let zeiger = 0;
  el.innerHTML = `
    <h2>Kontext im Blick</h2>
    <p class="tm-anleitung">${esc(daten.texte.anleitung)}</p>
    <div class="kt-schalter">${Object.entries(daten.werkzeuge).map(([id, w]) => `<button type="button" data-w="${id}" aria-pressed="${id === wahl}">${esc(w.name)}</button>`).join('')}</div>
    <div class="tm-fenster">
      <div class="tm-leiste" aria-hidden="true"><i></i><i></i><i></i><span class="kt-titel"></span></div>
      <pre class="tm-ausgabe kt-ausgabe" aria-live="polite"></pre>
      <div class="kt-anzeige"><span class="kt-balken"><span></span></span><span class="kt-zahl"></span></div>
      <form class="tm-zeile"><label><span class="tm-prompt">&gt;</span><input type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Eingabe: Auftrag oder Befehl mit Schrägstrich"></label></form>
    </div>
    <div class="tm-tasten kt-tasten" aria-label="Schnelltasten"></div>
    <p class="tm-geschafft" hidden></p>
    <table class="ca-vergleich kt-vergleich"><caption>${esc(daten.texte.vergleich)}</caption>
      <thead><tr><th scope="col">Wofür</th>${Object.values(daten.werkzeuge).map((w) => `<th scope="col">${esc(w.name)}</th>`).join('')}</tr></thead>
      <tbody>${daten.vergleich.map((v) => `<tr><th scope="row">${esc(v.zweck)}</th>${Object.keys(daten.werkzeuge).map((id) => `<td data-spalte="${esc(daten.werkzeuge[id].name)}">${esc(v[id]).replace(/(\/[a-z]+)/g, '<code>$1</code>')}</td>`).join('')}</tr>`).join('')}</tbody></table>
    <p class="ew-hinweis">${esc(daten.texte.hinweis)}</p>`;
  const aus = el.querySelector('.kt-ausgabe');
  const feld = el.querySelector('input');
  function anzeige() {
    const p = belegt(z, daten);
    const b = el.querySelector('.kt-balken span');
    b.style.width = `${p}%`;
    b.classList.toggle('eng', p >= daten.warnung);
    el.querySelector('.kt-zahl').textContent = anzeigeText(z, daten);
  }
  function neuAufbauen() {
    const w = daten.werkzeuge[wahl];
    el.querySelectorAll('[data-w]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.w === wahl)));
    el.querySelector('.kt-titel').textContent = `${w.name} (Nachbau)`;
    aus.textContent = `${w.texte.willkommen}\n`;
    el.querySelector('.kt-tasten').innerHTML = [`<button type="button" class="kt-arbeit" data-befehl="">${esc(daten.texte.weiter)}</button>`,
      ...w.tasten.map((t) => `<button type="button" data-befehl="${esc(t)}">${esc(t)}</button>`)].join('');
    el.querySelector('.tm-geschafft').hidden = true;
    anzeige();
  }
  function los(eingabe) {
    const naechster = daten.arbeit[z.schritt % daten.arbeit.length];
    const zeile = eingabe.trim() || naechster.prompt;
    const r = fuehreAus(zeile, z, daten);
    z = r.zustand;
    verlauf.push(zeile); zeiger = verlauf.length;
    // Anhängen statt ersetzen: aria-live liest so nur das Neue vor.
    if (r.leeren) aus.replaceChildren();
    aus.append(document.createTextNode(`> ${zeile}\n${r.ausgabe.length ? r.ausgabe.join('\n') + '\n' : ''}\n`));
    aus.scrollTop = aus.scrollHeight;
    anzeige();
    const g = el.querySelector('.tm-geschafft');
    if (g.hidden && z.benutzt.includes('compact') && z.benutzt.includes('neu')) {
      g.innerHTML = `<b>Geschafft.</b> ${esc(daten.texte.geschafft)}`;
      g.hidden = false;
    }
  }
  el.querySelector('.kt-schalter').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-w]');
    if (!b || b.dataset.w === wahl) return;
    wahl = b.dataset.w;
    z = startzustand(wahl);
    neuAufbauen();
  });
  el.querySelector('form').addEventListener('submit', (ev) => { ev.preventDefault(); if (feld.value.trim()) los(feld.value); feld.value = ''; });
  feld.addEventListener('keydown', (ev) => {
    if (ev.key === 'ArrowUp' && zeiger > 0) { zeiger--; feld.value = verlauf[zeiger]; ev.preventDefault(); }
    if (ev.key === 'ArrowDown' && zeiger < verlauf.length) { zeiger++; feld.value = verlauf[zeiger] ?? ''; ev.preventDefault(); }
  });
  el.querySelector('.kt-tasten').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-befehl]');
    if (b) los(b.dataset.befehl);
  });
  neuAufbauen();
}
