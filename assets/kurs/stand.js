// Fortschritt im KI-Kurs: welche Linie empfohlen ist, wo man eingestiegen ist, welche
// Stationen man besucht hat. Reine Logik ohne DOM, damit Node sie prüfen kann.
//
// Der Stand reist als Fragment mit (#stand=…): Es wird nie an einen Server geschickt und legt
// nichts auf dem Gerät ab. Format: 1~<linie|->~<start|->~<id,id,…>

const VERSION = '1';
const LINIEN = ['E', 'A', 'B'];

export function leererStand() {
  return {linie: null, start: null, besucht: []};
}

export function besuche(stand, id) {
  if (stand.besucht.includes(id)) return stand;
  return {...stand, besucht: [...stand.besucht, id]};
}

export function kodiere(stand) {
  return [VERSION, stand.linie ?? '-', stand.start ?? '-', stand.besucht.join(',')].join('~');
}

export function dekodiere(text, bekannteIds) {
  if (typeof text !== 'string') return null;
  const teile = text.split('~');
  if (teile.length !== 4 || teile[0] !== VERSION) return null;
  const [, linie, start, besucht] = teile;
  const bekannt = new Set(bekannteIds);
  const liste = [];
  for (const id of besucht ? besucht.split(',') : []) {
    if (bekannt.has(id) && !liste.includes(id)) liste.push(id);
  }
  return {
    linie: LINIEN.includes(linie) ? linie : null,
    start: bekannt.has(start) ? start : null,
    besucht: liste,
  };
}

export function alsFragment(stand) {
  return `#stand=${kodiere(stand)}`;
}

export function ausFragment(hash, bekannteIds) {
  if (typeof hash !== 'string' || !hash.startsWith('#stand=')) return null;
  let roh;
  try {
    roh = decodeURIComponent(hash.slice('#stand='.length));
  } catch {
    return null;
  }
  return dekodiere(roh, bekannteIds);
}

// Fortschritt aus dem Link und gemerkter Fortschritt ergänzen sich: Linie und Einstieg nimmt
// der erste, der sie kennt; besuchte Stationen werden zusammengelegt.
export function vereinige(a, b) {
  if (!a) return b ?? null;
  if (!b) return a;
  const besucht = [...a.besucht];
  for (const id of b.besucht) if (!besucht.includes(id)) besucht.push(id);
  return {linie: a.linie ?? b.linie, start: a.start ?? b.start, besucht};
}
