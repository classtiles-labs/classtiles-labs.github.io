// Erlebnis „Agent im Ordner“: ein Agent räumt einen Belegordner auf. Welche Rechte er bekommt,
// entscheidest du; was er ohne Recht nicht darf, überspringt er und sagt es. Beispiel, nachgestellt.

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const euro = (cent) => `${Math.floor(cent / 100)},${String(cent % 100).padStart(2, '0')} €`;

export function ausfuehren(dateien, schritte, rechte) {
  let liste = [...dateien];
  const protokoll = [];
  if (!rechte.has('lesen')) {
    return {dateien: liste, protokoll: ['Kein Leserecht: Der Agent sieht die Dateien nicht und kann nichts tun.'], tabelle: false};
  }
  let tabelle = false;
  for (const s of schritte) {
    if (s.art === 'lesen') protokoll.push(s.text);
    else if (s.art === 'umbenennen') {
      if (rechte.has('verschieben')) {
        liste = liste.map((d) => s.paare.find(([alt]) => alt === d)?.[1] ?? d);
        protokoll.push(s.text);
      } else protokoll.push('Darf nicht umbenennen: Die Namen bleiben, wie sie sind.');
    } else if (s.art === 'duplikat') {
      if (rechte.has('loeschen')) {
        liste = liste.filter((d) => d !== s.datei);
        protokoll.push(`${s.text} Löscht sie.`);
      } else if (rechte.has(s.ausweich)) {
        liste = liste.map((d) => (d === s.datei ? `Prüfen/${d}` : d));
        protokoll.push(`${s.text} Darf nicht löschen: legt sie in den Unterordner „Prüfen“.`);
      } else protokoll.push(`${s.text} Darf sie weder löschen noch verschieben: meldet sie dir nur.`);
    } else if (s.art === 'anlegen') {
      if (rechte.has('anlegen')) {
        liste.push(s.datei);
        tabelle = true;
        protokoll.push(s.text);
      } else protokoll.push('Darf nichts anlegen: Die Übersicht steht nur im Chat.');
    }
  }
  return {dateien: liste, protokoll, tabelle};
}

function fazit(rechte) {
  if (!rechte.has('lesen')) return 'Ohne Leserecht geht nichts. Lesen ist das Mindeste, was ein Agent im Ordner braucht.';
  if (rechte.has('loeschen')) return 'Mit Löschrecht ist die Kopie weg. Hier war es wirklich ein Duplikat. Hätte sich der Agent geirrt, wäre ein Beleg verloren. Löschen gibst du am besten gar nicht frei.';
  if (rechte.has('verschieben') && rechte.has('anlegen')) return 'So ist es sicher: Nichts ist verloren, die Kopie wartet in „Prüfen“ auf deinen Blick, die Übersicht liegt bereit.';
  return 'Mit weniger Rechten erledigt der Agent weniger. Was er nicht darf, sagt er dir.';
}

const ordner = (liste, neu = []) => liste.map((d) => `<li${neu.includes(d) ? ' class="neu"' : ''}>${esc(d)}</li>`).join('');

export function mount(el, daten) {
  if (!daten?.dateien?.length) return;
  const rechte = new Set(daten.rechte.filter((r) => r.an).map((r) => r.id));
  el.innerHTML = `
    <h2>Was darf der Agent?</h2>
    <p class="oa-anleitung">Im Ordner „${esc(daten.ordner)}“ liegen Belege einer Klassenfahrt. Der Auftrag: „${esc(daten.auftrag)}“ Wähle die Rechte und lass den Agenten arbeiten.</p>
    <div class="oa-rechte">${daten.rechte.map((r) => `<button type="button" class="pb-chip${r.an ? ' an' : ''}" data-recht="${r.id}" aria-pressed="${r.an}">${esc(r.name)}</button>`).join('')}</div>
    <button type="button" class="btn b-solid" data-los>Auftrag ausführen</button>
    <div class="oa-raster">
      <div><p class="pb-label">Vorher</p><ul class="oa-ordner">${ordner(daten.dateien)}</ul></div>
      <div><p class="pb-label">Nachher</p><ul class="oa-ordner oa-nachher"><li class="leer">noch nicht ausgeführt</li></ul></div>
    </div>
    <ol class="oa-protokoll" aria-live="polite"></ol>
    <table class="oa-tabelle" hidden><caption>Übersicht.csv</caption>
      <thead><tr><th>Datum</th><th>Art</th><th>Betrag</th></tr></thead>
      <tbody>${daten.belege.map((b) => `<tr><td>${b.datum.split('-').reverse().join('.')}</td><td>${esc(b.art)}</td><td>${euro(b.cent)}</td></tr>`).join('')}</tbody>
      <tfoot><tr><th colspan="2">Summe</th><td>${euro(daten.summeCent)}</td></tr></tfoot></table>
    <p class="oa-fazit" hidden></p>
    <p class="ew-hinweis">${esc(daten.hinweis)}</p>`;
  const nachher = el.querySelector('.oa-nachher');
  const protokoll = el.querySelector('.oa-protokoll');
  const zuruecksetzen = () => {
    nachher.innerHTML = '<li class="leer">noch nicht ausgeführt</li>';
    protokoll.innerHTML = '';
    el.querySelector('.oa-tabelle').hidden = true;
    el.querySelector('.oa-fazit').hidden = true;
  };
  el.querySelector('.oa-rechte').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-recht]');
    if (!b) return;
    const an = !rechte.has(b.dataset.recht);
    if (an) rechte.add(b.dataset.recht); else rechte.delete(b.dataset.recht);
    b.classList.toggle('an', an);
    b.setAttribute('aria-pressed', String(an));
    zuruecksetzen();
  });
  el.querySelector('[data-los]').addEventListener('click', () => {
    const r = ausfuehren(daten.dateien, daten.schritte, rechte);
    nachher.innerHTML = ordner(r.dateien, r.dateien.filter((d) => !daten.dateien.includes(d)));
    protokoll.innerHTML = r.protokoll.map((p) => `<li>${esc(p)}</li>`).join('');
    el.querySelector('.oa-tabelle').hidden = !r.tabelle;
    const f = el.querySelector('.oa-fazit');
    f.textContent = fazit(rechte);
    f.hidden = false;
  });
}
