// Layout des Liniennetzes: drei waagerechte Linien (E, A, B) übereinander, Stationen von
// links nach rechts, Beschriftungen schräg darüber. Reine Rechnung ohne DOM — gezeichnet wird in
// kurs.js. Die Abstände ergeben sich aus der Breite, damit auch bei 320 px kein Name über den
// Rand ragt (Schätzung: 6,2 px je Zeichen bei 11 px Schrift).

export const WINKEL = 38;
const ZEICHEN_PX = 6.2;
const X0 = 46;          // erste Station, rechts neben dem Linien-Schild
const LABEL_DX = 4;     // Beschriftung beginnt leicht rechts über der Station
const LABEL_DY = 16;
const RAND = 8;
const ABSTAND = 46;     // Platz unter einer Linie für die Zug-Marke
const LINIEN = ['E', 'A', 'B'];

const r1 = (n) => Math.round(n * 10) / 10;
// Waagerecht wird abgerundet: Aufrunden schöbe das letzte Label um Bruchteile über den Rand.
const ab = (n) => Math.floor(n * 10) / 10;

export function netzLayout(netz, {breite = 390} = {}) {
  const rad = (WINKEL * Math.PI) / 180;
  const cos = Math.cos(rad), sin = Math.sin(rad);
  const out = {hoehe: 0, linien: [], stationen: [], umstiege: [], labels: [], schilder: []};
  let y = 0;

  for (const [n, lid] of LINIEN.entries()) {
    const st = netz.stationen.filter((s) => s.linie === lid);
    if (!st.length) continue;
    const laenge = st.map((s) => s.titel.length * ZEICHEN_PX);
    const anstieg = Math.max(...laenge.map((l) => sin * l)) + LABEL_DY + 12;
    y = n === 0 ? anstieg + 6 : y + ABSTAND + anstieg;

    let schritt = st.length > 1 ? (breite - RAND - 16 - X0) / (st.length - 1) : 0;
    for (let i = 1; i < st.length; i++) {
      schritt = Math.min(schritt, (breite - RAND - LABEL_DX - cos * laenge[i] - X0) / i);
    }
    st.forEach((s, i) => {
      const x = X0 + i * schritt;
      out.stationen.push({id: s.id, titel: s.titel, linie: lid, x: ab(x), y: r1(y),
        umstieg: s.umstieg ?? null, geplant: s.status !== 'gebaut'});
      out.labels.push({id: s.id, x: ab(x + LABEL_DX), y: r1(y - LABEL_DY), winkel: -WINKEL,
        laengeGeschaetzt: laenge[i]});
    });
    const letzte = X0 + (st.length - 1) * schritt;
    out.linien.push({id: lid, y: r1(y), x1: X0 - 10, x2: r1(Math.min(letzte + 14, breite - RAND))});
    out.schilder.push({linie: lid, x: 6, y: r1(y)});
  }

  const finde = (id) => out.stationen.find((s) => s.id === id);
  for (const s of out.stationen) {
    if (!s.umstieg) continue;
    const z = finde(s.umstieg);
    if (!z) continue;
    const mitte = r1((s.y + z.y) / 2);
    out.umstiege.push({von: s.id, nach: z.id,
      pfad: `M${s.x} ${s.y} C${s.x} ${mitte} ${z.x} ${mitte} ${z.x} ${z.y}`});
  }
  out.hoehe = r1(y + ABSTAND);
  return out;
}

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// Das gezeichnete Netz als SVG-Text. `fragment` (z. B. „#stand=…“) hängt an jedem
// Stationslink, damit der Fortschritt auch beim Tippen ins Netz mitreist.
export function netzSvg(netz, stand, fragment, breite) {
  const l = netzLayout(netz, {breite});
  const besucht = new Set(stand.besucht);
  const zug = [...stand.besucht].reverse().find((id) => l.stationen.some((s) => s.id === id)) ?? stand.start;
  const teile = [];
  for (const u of l.umstiege) teile.push(`<path class="netz-umstieg" d="${u.pfad}"/>`);
  for (const li of l.linien) {
    teile.push(`<line class="netz-linie linie-${li.id.toLowerCase()}" x1="${li.x1}" y1="${li.y}" x2="${li.x2}" y2="${li.y}"/>`);
  }
  for (const sch of l.schilder) {
    teile.push(`<g class="netz-schild linie-${sch.linie.toLowerCase()}"><rect x="${sch.x}" y="${sch.y - 12}" width="28" height="24" rx="6"/><text x="${sch.x + 14}" y="${sch.y + 5}">${sch.linie}</text></g>`);
  }
  for (const s of l.stationen) {
    const klasse = ['netz-station', `linie-${s.linie.toLowerCase()}`];
    if (s.geplant) klasse.push('geplant');
    if (besucht.has(s.id)) klasse.push('besucht');
    if (s.umstieg) klasse.push('umsteige');
    const form = s.umstieg
      ? `<rect class="${klasse.join(' ')}" x="${s.x - 9}" y="${s.y - 9}" width="18" height="18" rx="9"/>`
      : `<circle class="${klasse.join(' ')}" cx="${s.x}" cy="${s.y}" r="7"/>`;
    teile.push(s.geplant ? form : `<a href="ki-kurs-${s.id}.html${fragment}" tabindex="-1">${form}</a>`);
  }
  for (const lab of l.labels) {
    const s = l.stationen.find((x) => x.id === lab.id);
    teile.push(`<text class="netz-label${s.geplant ? ' geplant' : ''}" x="${lab.x}" y="${lab.y}" transform="rotate(${lab.winkel} ${lab.x} ${lab.y})">${esc(s.titel)}</text>`);
  }
  const z = l.stationen.find((s) => s.id === zug);
  if (z) {
    teile.push(`<circle class="netz-puls linie-${z.linie.toLowerCase()}" cx="${z.x}" cy="${z.y}" r="9"/>`);
    teile.push(`<g class="netz-zug"><rect x="${z.x - 20}" y="${z.y + 14}" width="40" height="18" rx="9"/><text x="${z.x}" y="${z.y + 27}">Du</text></g>`);
  }
  return `<svg viewBox="0 0 ${breite} ${l.hoehe}" width="100%" aria-hidden="true" focusable="false">${teile.join('')}</svg>`;
}
