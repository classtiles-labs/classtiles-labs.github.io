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
