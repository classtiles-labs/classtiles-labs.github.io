import {test} from 'node:test';
import assert from 'node:assert/strict';
import {tippe, prompt} from '../../../assets/kurs/erlebnisse/prompt-baukasten.js';
import {daten} from './hilfen.mjs';

const D = daten('prompt-baukasten');

test('Bausteine wirken kumulativ in fester Reihenfolge', () => {
  assert.equal(tippe(0, 2), 3);   // Baustein 3 an → 1 bis 3 an
  assert.equal(tippe(3, 2), 2);   // Baustein 3 aus → 3 und danach aus
  assert.equal(tippe(3, 0), 0);
  assert.equal(tippe(1, 3), 4);
  assert.equal(tippe(4, 3), 3);
});

test('n Bausteine, n+1 Antworten aus echten Läufen', () => {
  assert.equal(D.antworten.length, D.bausteine.length + 1);
  for (const a of D.antworten) {
    assert.ok(a.text.trim().length > 40);
    for (const k of ['app', 'modell', 'datum']) assert.ok(a[k], `${k} fehlt`);
    assert.match(a.datum, /^\d{4}-\d{2}-\d{2}$/);
  }
  assert.ok(D.bausteine.every((b) => b.name && b.text));
});

test('der Prompt wächst mit den Bausteinen', () => {
  assert.equal(prompt(D, 0), D.basis);
  const voll = prompt(D, D.bausteine.length);
  let pos = -1;
  for (const b of D.bausteine) {
    const p = voll.indexOf(b.text);
    assert.ok(p > pos, `${b.name} fehlt oder steht falsch`);
    pos = p;
  }
});
