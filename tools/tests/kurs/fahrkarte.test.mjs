import {test} from 'node:test';
import assert from 'node:assert/strict';
import {auswerten} from '../../../assets/kurs/erlebnisse/fahrkarte.js';
import {daten} from './hilfen.mjs';

const D = daten('fahrkarte');

test('genau drei Fragen in der Reihenfolge E, A, B', () => {
  assert.deepEqual(D.fragen.map((f) => f.linie), ['E', 'A', 'B']);
});

test('jede Frage: 3–4 Antworten, genau eine richtig, Erklärung vorhanden', () => {
  for (const f of D.fragen) {
    assert.ok(f.frage.trim().endsWith('?'), f.frage);
    assert.ok(f.antworten.length >= 3 && f.antworten.length <= 4, f.frage);
    assert.equal(f.antworten.filter((a) => a.richtig).length, 1, f.frage);
    assert.ok(f.erklaerung.trim().length > 40, f.frage);
    assert.ok(f.antworten.every((a) => a.text.trim()), f.frage);
  }
});

test('auswerten: alles richtig → Linie B, Terminal', () => {
  const richtig = D.fragen.map((f) => f.antworten.findIndex((a) => a.richtig));
  const r = auswerten(D, richtig);
  assert.deepEqual(r.ergebnisse, ['richtig', 'richtig', 'richtig']);
  assert.deepEqual(r.empfehlung, {linie: 'B', station: 'terminal'});
});

test('auswerten: „weiß ich nicht“ und falsche Antworten', () => {
  const falsch = D.fragen.map((f) => f.antworten.findIndex((a) => !a.richtig));
  assert.deepEqual(auswerten(D, falsch).empfehlung, {linie: 'E', station: 'wie-ki-schreibt'});
  const r = auswerten(D, ['weiss-nicht', 'weiss-nicht', 'weiss-nicht']);
  assert.deepEqual(r.ergebnisse, ['weiss-nicht', 'weiss-nicht', 'weiss-nicht']);
  const richtig0 = D.fragen[0].antworten.findIndex((a) => a.richtig);
  assert.deepEqual(auswerten(D, [richtig0, falsch[1], 'weiss-nicht']).empfehlung, {linie: 'E', station: 'gut-fragen'});
});
