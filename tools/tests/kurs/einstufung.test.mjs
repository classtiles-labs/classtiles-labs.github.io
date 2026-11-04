import {test} from 'node:test';
import assert from 'node:assert/strict';
import {empfehlung} from '../../../assets/kurs/einstufung.js';
import {ids} from './hilfen.mjs';

const R = 'richtig', F = 'falsch', W = 'weiss-nicht';

test('erster nicht richtiger Index bestimmt den Einstieg', () => {
  assert.deepEqual(empfehlung([F, R, R]), {linie: 'E', station: 'wie-ki-schreibt'});
  assert.deepEqual(empfehlung([W, R, R]), {linie: 'E', station: 'wie-ki-schreibt'});
  assert.deepEqual(empfehlung([R, F, R]), {linie: 'E', station: 'gut-fragen'});
  assert.deepEqual(empfehlung([R, R, W]), {linie: 'A', station: 'eigenes-material'});
  assert.deepEqual(empfehlung([R, R, R]), {linie: 'B', station: 'terminal'});
});

test('fehlende Antworten zählen als nicht richtig', () => {
  assert.deepEqual(empfehlung([]), {linie: 'E', station: 'wie-ki-schreibt'});
  assert.deepEqual(empfehlung([R]), {linie: 'E', station: 'gut-fragen'});
});

test('jede empfohlene Station gibt es im Register', () => {
  const IDS = ids();
  for (const e of [[F], [R, F], [R, R, F], [R, R, R]]) assert.ok(IDS.includes(empfehlung(e).station));
});
