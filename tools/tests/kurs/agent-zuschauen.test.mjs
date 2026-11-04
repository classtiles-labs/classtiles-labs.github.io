import {test} from 'node:test';
import assert from 'node:assert/strict';
import {naechsterSchritt} from '../../../assets/kurs/erlebnisse/agent-zuschauen.js';
import {daten} from './hilfen.mjs';

const D = daten('agent-zuschauen');

test('Ablauf: mindestens 5 Schritte, Freigaben mit beiden Ausgängen', () => {
  assert.ok(D.schritte.length >= 5);
  const frei = D.schritte.filter((s) => s.freigabe);
  assert.ok(frei.length >= 2);
  for (const s of frei) assert.ok(s.beiFreigabe && s.beiStopp, s.titel);
  assert.ok(frei.some((s) => /E-Mail|senden/i.test(s.titel)), 'eine Freigabe für etwas, das nach außen geht');
  assert.ok(frei.some((s) => /Klassenliste|Namen/i.test(s.titel + s.text)), 'eine Freigabe mit Schülerdaten');
  assert.equal(D.schritte.at(-1).art, 'fertig');
});

test('naechsterSchritt hält an Freigaben, bis entschieden ist', () => {
  const i = D.schritte.findIndex((s) => s.freigabe);
  const leer = new Map();
  assert.deepEqual(naechsterSchritt(D, i, leer), {index: i, wartetAufFreigabe: true});
  assert.equal(naechsterSchritt(D, i, new Map([[i, 'stopp']])).index, i + 1);
  assert.equal(naechsterSchritt(D, i, new Map([[i, 'frei']])).index, i + 1);
  assert.deepEqual(naechsterSchritt(D, i - 1, leer), {index: i, wartetAufFreigabe: true});
  const letzte = D.schritte.length - 1;
  assert.equal(naechsterSchritt(D, letzte, leer).index, letzte);
});
