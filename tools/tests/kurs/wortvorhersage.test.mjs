import {test} from 'node:test';
import assert from 'node:assert/strict';
import {verteilung, ziehe} from '../../../assets/kurs/erlebnisse/wortvorhersage.js';
import {daten} from './hilfen.mjs';

const P = [38, 24, 17, 11, 9.9, 0.1];
const summe = (a) => a.reduce((x, y) => x + y, 0);

test('verteilung ist normiert und behält die Reihenfolge', () => {
  const v = verteilung(P, 1);
  assert.ok(Math.abs(summe(v) - 1) < 1e-9);
  for (let i = 1; i < v.length; i++) assert.ok(v[i] <= v[i - 1]);
});

test('niedrige Temperatur stärkt das Wahrscheinlichste, hohe das Seltene', () => {
  const kalt = verteilung(P, 0.3), normal = verteilung(P, 1), heiss = verteilung(P, 2.5);
  assert.ok(kalt[0] > normal[0] && normal[0] > heiss[0]);
  assert.ok(heiss.at(-1) > normal.at(-1) && normal.at(-1) > kalt.at(-1));
  assert.ok(verteilung(P, 0.2)[0] > 0.85);
});

test('ziehe wählt nach Verteilung', () => {
  const v = [0.5, 0.3, 0.2];
  assert.equal(ziehe(v, 0), 0);
  assert.equal(ziehe(v, 0.49), 0);
  assert.equal(ziehe(v, 0.5), 1);
  assert.equal(ziehe(v, 0.85), 2);
  assert.equal(ziehe(v, 0.9999), 2);
});

test('Beispieldaten: Stufen summieren 95–100 %, Hinweis auf Beispielwerte', () => {
  const d = daten('wortvorhersage');
  assert.match(d.hinweis, /Beispielwerte/);
  assert.ok(d.stufen.length >= 2);
  for (const s of d.stufen) {
    const sum = summe(s.optionen.map(([, p]) => p));
    assert.ok(sum >= 95 && sum <= 100.0001, `Summe ${sum}`);
  }
  assert.ok(d.regler.min < d.regler.start && d.regler.start < d.regler.max);
});
