import {test} from 'node:test';
import assert from 'node:assert/strict';
import {duFormen} from '../../../assets/kurs/erlebnisse/feedback-check.js';
import {kennzahlen} from '../../../assets/kurs/erlebnisse/differenzieren.js';
import {daten} from './hilfen.mjs';

const D = daten('feedback-check');
const [schlicht, gezielt] = D.laeufe;

test('duFormen zählt du, dich, dir und dein…, aber keine Wortteile', () => {
  assert.equal(duFormen('Du schreibst. Dein Schluss passt zu dir, ich lobe dich und deine These.'), 5);
  assert.equal(duFormen('Die Schülerin schreibt dunkel und durchdacht.'), 0);
});

test('zwei echte Läufe mit Prompt, App, Modell und Datum', () => {
  assert.equal(D.laeufe.length, 2);
  for (const l of D.laeufe) {
    for (const k of ['prompt', 'text', 'app', 'modell', 'modus', 'datum']) assert.ok(l[k], `${l.id}.${k}`);
    assert.match(l.datum, /^\d{4}-\d{2}-\d{2}$/);
  }
});

test('die schlichte Bitte spricht über die Schülerin, die gezielte mit ihr', () => {
  assert.equal(duFormen(schlicht.text), 0);
  assert.ok(duFormen(gezielt.text) >= 3);
});

test('die gezielte Antwort ist weniger als halb so lang und hat die drei Teile', () => {
  assert.ok(kennzahlen(gezielt.text).woerter * 2 < kennzahlen(schlicht.text).woerter);
  for (const t of ['Ziel', 'Stand', 'Nächster Schritt']) assert.ok(gezielt.text.includes(t), t);
});

test('jede Antwort der Entscheidung hat eine Erklärung', () => {
  assert.ok(D.entscheidung.optionen.length >= 3);
  for (const o of D.entscheidung.optionen) assert.ok(o.text && o.erklaerung.length > 40);
});
