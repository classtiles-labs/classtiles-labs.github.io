import {test} from 'node:test';
import assert from 'node:assert/strict';
import {daten} from './hilfen.mjs';

const D = daten('vorher-nachher');

test('beide Antworten aus echten Läufen', () => {
  for (const seite of ['ohne', 'mit']) {
    for (const k of ['text', 'app', 'modell', 'datum', 'urteil']) assert.ok(D[seite][k], `${seite}.${k}`);
    assert.match(D[seite].datum, /^\d{4}-\d{2}-\d{2}$/);
  }
  assert.ok(D.bitte && D.schuelertext && D.dokument.titel && D.dokument.auszug);
});

test('mit Dokument greift die Antwort das Raster auf, ohne nicht', () => {
  const treffer = D.dokument.kriterien.filter((k) => D.mit.text.includes(k));
  assert.ok(treffer.length >= 3, `nur ${treffer}`);
  assert.ok(!D.ohne.text.includes('/ 16') && !D.ohne.text.includes('von 16'));
});
