// Erlebnis „Differenzieren“: ein Sachtext in vier Klassenstufen, per Regler umschaltbar.
// Die Fassungen 5, 6/7 und 10 stammen aus einem echten Lauf, die Kennzahlen rechnet die Seite.

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const datum = (iso) => iso.split('-').reverse().join('.');

// Zahlen wie „30 000“ zählen als ein Wort, Bindestrich-Wörter auch.
const WORT = /\d{1,3}(?:[  ]\d{3})+|[\p{L}\d]+(?:-[\p{L}\d]+)*/gu;

export function kennzahlen(text) {
  const woerter = String(text).match(WORT) ?? [];
  const saetze = String(text).split(/[.!?]+(?=\s|$)/).filter((s) => /[\p{L}\d]/u.test(s));
  if (!woerter.length || !saetze.length) return {woerter: 0, saetze: 0, wps: 0, lange: 0, lix: 0};
  const lange = woerter.filter((w) => (w.match(/\p{L}/gu) ?? []).length > 6).length;
  const wps = woerter.length / saetze.length;
  return {
    woerter: woerter.length,
    saetze: saetze.length,
    wps: Math.round(wps * 10) / 10,
    lange,
    lix: Math.round(wps + (100 * lange) / woerter.length),
  };
}

export function mount(el, daten) {
  if (!daten?.stufen?.length) return;
  const start = daten.stufen.findIndex((s) => s.quelle === 'ausgangstext');
  let i = start < 0 ? 0 : start;
  el.innerHTML = `
    <h2>Ein Text, vier Klassenstufen</h2>
    <p class="df-anleitung">Zieh den Regler. Derselbe Sachtext, von ${esc(daten.lauf.app)} umgeschrieben. Die Zahlen darunter rechnet diese Seite live aus.</p>
    <label class="ew-regler df-regler">Klasse ${esc(daten.stufen[0].klasse)}
      <input type="range" min="0" max="${daten.stufen.length - 1}" step="1" value="${i}" aria-label="Klassenstufe">
      Klasse ${esc(daten.stufen[daten.stufen.length - 1].klasse)}</label>
    <p class="df-stufe" aria-live="polite"></p>
    <h3 class="df-titel">${esc(daten.titel)}</h3>
    <p class="df-text"></p>
    <div class="df-pruef" hidden><b>Prüfstelle:</b> ${esc(daten.pruefstelle.erklaerung)}</div>
    <dl class="df-zahlen"></dl>
    <p class="ew-hinweis">${esc(daten.hinweis)} ${esc(daten.lauf.modell)}, ${esc(daten.lauf.modus)}, ${datum(daten.lauf.datum)}. LIX: Lesbarkeitsindex aus Satzlänge und Anteil langer Wörter, je höher, desto schwerer.</p>
    <details class="vn-text"><summary>Der Auftrag an ${esc(daten.lauf.app)}</summary><pre>${esc(daten.lauf.auftrag)}</pre></details>`;
  const regler = el.querySelector('input[type=range]');
  function zeichne() {
    const s = daten.stufen[i];
    const p = daten.pruefstelle;
    const pruefen = p && p.klasse === s.klasse && s.text.includes(p.zitat);
    const text = esc(s.text);
    el.querySelector('.df-text').innerHTML = pruefen ? text.replace(esc(p.zitat), `<mark class="df-mark">${esc(p.zitat)}</mark>`) : text;
    el.querySelector('.df-pruef').hidden = !pruefen;
    const herkunft = s.quelle === 'ausgangstext' ? 'Ausgangstext' : `Fassung von ${daten.lauf.app}`;
    el.querySelector('.df-stufe').innerHTML = `<b>Klasse ${esc(s.klasse)}</b> · ${herkunft}`;
    regler.setAttribute('aria-valuetext', `Klasse ${s.klasse}`);
    const k = kennzahlen(s.text);
    el.querySelector('.df-zahlen').innerHTML = [
      ['Wörter', k.woerter], ['Sätze', k.saetze], ['Wörter pro Satz', String(k.wps).replace('.', ',')], ['Lange Wörter', k.lange], ['LIX', k.lix],
    ].map(([n, v]) => `<div><dt>${n}</dt><dd>${v}</dd></div>`).join('');
  }
  regler.addEventListener('input', () => { i = Number(regler.value); zeichne(); });
  zeichne();
}
