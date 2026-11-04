import {test} from 'node:test';
import assert from 'node:assert/strict';
import {pruefeTreffer, stellen} from '../../../assets/kurs/erlebnisse/erwisch-die-ki.js';
import {daten} from './hilfen.mjs';

const D = daten('erwisch-die-ki');
const WOCHENTAGE = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];
const wochentag = (iso) => WOCHENTAGE[new Date(`${iso}T12:00:00Z`).getUTCDay()];

test('genau drei Fehler und mindestens zwei Ablenker, alle mit Erklärung', () => {
  const s = stellen(D);
  assert.equal(s.filter((x) => x.art === 'fehler').length, 3);
  assert.ok(s.filter((x) => x.art === 'ablenker').length >= 2);
  for (const x of s) assert.ok(x.erklaerung.length > 20, x.id);
  assert.equal(new Set(s.map((x) => x.id)).size, s.length);
  assert.match(D.hinweis, /Beispiel/);
});

test('die Fehler sind wirklich falsch, die Ablenker wirklich richtig', () => {
  for (const x of stellen(D)) {
    if (!x.pruefe) continue;
    let stimmt;
    if (x.pruefe.datum) stimmt = wochentag(x.pruefe.datum) === x.pruefe.behauptet;
    if (x.pruefe.faktoren) stimmt = x.pruefe.faktoren.reduce((a, b) => a * b, 1) === x.pruefe.behauptet;
    assert.equal(stimmt, x.art === 'ablenker', `${x.id}: Prüfung passt nicht zur Art`);
  }
  assert.ok(stellen(D).filter((x) => x.pruefe).length >= 3);
});

test('pruefeTreffer', () => {
  const f = stellen(D).find((x) => x.art === 'fehler');
  assert.deepEqual(pruefeTreffer(D, f.id), {fehler: true, erklaerung: f.erklaerung});
  const a = stellen(D).find((x) => x.art === 'ablenker');
  assert.equal(pruefeTreffer(D, a.id).fehler, false);
  assert.equal(pruefeTreffer(D, 'gibt-es-nicht'), null);
});
