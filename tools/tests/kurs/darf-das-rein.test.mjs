import {test} from 'node:test';
import assert from 'node:assert/strict';
import {bewerte} from '../../../assets/kurs/erlebnisse/darf-das-rein.js';
import {daten} from './hilfen.mjs';

const D = daten('darf-das-rein');

test('mindestens 6 Karten, gemischt, jede mit Begründung', () => {
  assert.ok(D.karten.length >= 6);
  assert.ok(D.karten.filter((k) => k.ok).length >= 2);
  assert.ok(D.karten.filter((k) => !k.ok).length >= 2);
  for (const k of D.karten) assert.ok(k.warum.length > 20, k.text);
  assert.ok(D.karten.some((k) => !k.ok && /Name/.test(k.text)), 'eine Karte zu Schülerdaten mit Namen');
  assert.match(D.hinweis, /keine Rechtsberatung/);
});

test('bewerte', () => {
  const k = D.karten.find((x) => !x.ok);
  assert.deepEqual(bewerte(k, false), {richtig: true, warum: k.warum});
  assert.equal(bewerte(k, true).richtig, false);
});
