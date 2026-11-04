import {test} from 'node:test';
import assert from 'node:assert/strict';
import {netzLayout, WINKEL} from '../../../assets/kurs/netz.js';
import {netz} from './hilfen.mjs';

const N = netz();
const rad = (WINKEL * Math.PI) / 180;

for (const breite of [320, 390, 640]) {
  test(`Beschriftungen bleiben im Netz bei ${breite} px (Review Focus 4)`, () => {
    const l = netzLayout(N, {breite});
    assert.equal(l.labels.length, N.stationen.length);
    for (const lab of l.labels) {
      assert.ok(lab.x + Math.cos(rad) * lab.laengeGeschaetzt <= breite - 8, `${lab.id} rechts über den Rand`);
      assert.ok(lab.y - Math.sin(rad) * lab.laengeGeschaetzt >= 0, `${lab.id} oben über den Rand`);
    }
    assert.ok(l.hoehe > 0);
  });
}

test('Stationen einer Linie liegen auf einer Höhe, von links nach rechts', () => {
  const l = netzLayout(N, {breite: 390});
  for (const lid of ['E', 'A', 'B']) {
    const st = l.stationen.filter((s) => s.linie === lid);
    assert.ok(st.length > 0);
    assert.ok(st.every((s) => s.y === st[0].y));
    for (let i = 1; i < st.length; i++) assert.ok(st[i].x > st[i - 1].x);
  }
  const ys = ['E', 'A', 'B'].map((lid) => l.linien.find((x) => x.id === lid).y);
  assert.ok(ys[0] < ys[1] && ys[1] < ys[2]);
});

test('jeder Umstieg ergibt genau einen Pfad', () => {
  const l = netzLayout(N, {breite: 390});
  const mitUmstieg = N.stationen.filter((s) => s.umstieg);
  assert.equal(l.umstiege.length, mitUmstieg.length);
  for (const s of mitUmstieg) {
    const u = l.umstiege.filter((x) => x.von === s.id);
    assert.equal(u.length, 1);
    assert.equal(u[0].nach, s.umstieg);
    assert.match(u[0].pfad, /^M[\d.]+ [\d.]+ C/);
  }
});

test('geplante Stationen sind markiert', () => {
  const l = netzLayout(N, {breite: 390});
  for (const s of N.stationen) assert.equal(l.stationen.find((x) => x.id === s.id).geplant, s.status !== 'gebaut');
});

test('Stationslinks im gezeichneten Netz tragen den Stand mit (Schlussprüfung, Fund 1)', async () => {
  const {netzSvg} = await import('../../../assets/kurs/netz.js');
  const N2 = structuredClone(N);
  N2.stationen.find((s) => s.id === 'wie-ki-schreibt').status = 'gebaut';
  const svg = netzSvg(N2, {linie: 'E', start: 'wie-ki-schreibt', besucht: ['wie-ki-schreibt']}, '#stand=1~E~wie-ki-schreibt~wie-ki-schreibt', 390);
  assert.match(svg, /href="ki-kurs-wie-ki-schreibt\.html#stand=1~E~wie-ki-schreibt~wie-ki-schreibt"/);
  assert.doesNotMatch(svg, /href="ki-kurs-[a-z-]+\.html"/, 'kein Stationslink ohne Stand');
  const leer = netzSvg(N2, {linie: null, start: null, besucht: []}, '', 390);
  assert.match(leer, /href="ki-kurs-wie-ki-schreibt\.html"/);
});
