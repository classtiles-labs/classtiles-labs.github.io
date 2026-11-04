import {test} from 'node:test';
import assert from 'node:assert/strict';
import {kennzahlen} from '../../../assets/kurs/erlebnisse/differenzieren.js';
import {daten} from './hilfen.mjs';

const D = daten('differenzieren');

test('kennzahlen zählt Wörter, Sätze, lange Wörter und den LIX', () => {
  const k = kennzahlen('Der Hund bellt laut. Die Nachbarskatze schläft trotzdem weiter!');
  assert.equal(k.woerter, 9);
  assert.equal(k.saetze, 2);
  assert.equal(k.wps, 4.5);
  assert.equal(k.lange, 3); // schläft, Nachbarskatze, trotzdem
  assert.equal(k.lix, Math.round(4.5 + 100 * 3 / 9));
});

test('Zahlen mit Leerzeichen und Klammern stören die Zählung nicht', () => {
  const k = kennzahlen('Bis zu 30 000 Grad (sehr heiß).');
  assert.equal(k.saetze, 1);
  assert.equal(k.woerter, 6);
});

test('leerer Text ergibt Nullen statt NaN', () => {
  assert.deepEqual(kennzahlen(''), {woerter: 0, saetze: 0, wps: 0, lange: 0, lix: 0});
});

test('vier Stufen von Klasse 5 bis 10, LIX steigt streng', () => {
  assert.deepEqual(D.stufen.map((s) => s.klasse), ['5', '6/7', '8', '10']);
  const lix = D.stufen.map((s) => kennzahlen(s.text).lix);
  for (let i = 1; i < lix.length; i++) assert.ok(lix[i] > lix[i - 1], `LIX ${lix}`);
});

test('jede Fassung behält die Fachbegriffe, Klasse 10 hat zwei mehr', () => {
  for (const s of D.stufen) for (const w of ['Aufwind', 'Gewitterwolke', 'Blitz', 'Donner']) assert.ok(s.text.includes(w), `${s.klasse}: ${w}`);
  const k10 = D.stufen.find((s) => s.klasse === '10').text;
  assert.ok(k10.includes('Kondensation') && k10.includes('Ladungstrennung'));
});

test('der Lauf ist echt beschriftet, der Ausgangstext als eigener markiert', () => {
  for (const k of ['app', 'modell', 'datum', 'auftrag']) assert.ok(D.lauf[k], k);
  assert.match(D.lauf.datum, /^\d{4}-\d{2}-\d{2}$/);
  assert.equal(D.stufen.find((s) => s.klasse === '8').quelle, 'ausgangstext');
});

test('die Prüfstelle steht wörtlich in ihrer Stufe und hat eine Erklärung', () => {
  const s = D.stufen.find((x) => x.klasse === D.pruefstelle.klasse);
  assert.ok(s.text.includes(D.pruefstelle.zitat));
  assert.ok(D.pruefstelle.erklaerung.length > 40);
});
