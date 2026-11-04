import {test} from 'node:test';
import assert from 'node:assert/strict';
import {sichtbar, belegt} from '../../../assets/kurs/erlebnisse/kontextfenster.js';
import {daten} from './hilfen.mjs';

const n = (k, t) => Array.from({length: k}, () => ({tokens: t}));

test('älteste Nachrichten fallen zuerst heraus', () => {
  assert.equal(sichtbar(n(5, 30), 100), 2);
  assert.equal(sichtbar(n(3, 30), 100), 0);
  assert.equal(sichtbar([], 100), 0);
  assert.equal(belegt(n(5, 30), 2), 90);
});

test('Beispiel: Die wichtige erste Nachricht fällt genau mit der vergesslichen Antwort heraus', () => {
  const d = daten('kontextfenster');
  assert.match(d.hinweis, /Vereinfachtes Beispiel/);
  const m = d.nachrichten;
  assert.ok(m[0].wichtig, 'erste Nachricht trägt die Vorgabe');
  const letzte = m.length - 1;
  assert.ok(m[letzte].vergessen, 'letzte Antwort zeigt das Vergessen');
  assert.equal(sichtbar(m.slice(0, letzte), d.fenster), 0, 'vorher passt alles hinein');
  assert.ok(sichtbar(m, d.fenster) > 0, 'mit der letzten Antwort fällt der Anfang heraus');
  assert.ok(m.every((x) => x.tokens > 0 && x.text && ['du', 'ki'].includes(x.wer)));
});
