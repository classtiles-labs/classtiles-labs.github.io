import {test} from 'node:test';
import assert from 'node:assert/strict';
import {ausfuehren} from '../../../assets/kurs/erlebnisse/ordner-agent.js';
import {daten} from './hilfen.mjs';

const D = daten('ordner-agent');
const alle = new Set(['lesen', 'anlegen', 'verschieben', 'loeschen']);
const empfohlen = new Set(['lesen', 'anlegen', 'verschieben']);
const dup = D.schritte.find((s) => s.art === 'duplikat').datei;

test('ohne Leserecht passiert nichts', () => {
  const r = ausfuehren(D.dateien, D.schritte, new Set(['anlegen', 'verschieben', 'loeschen']));
  assert.deepEqual(r.dateien, D.dateien);
  assert.equal(r.protokoll.length, 1);
});

test('ohne Löschrecht geht keine Datei verloren, das Duplikat landet in Prüfen/', () => {
  const r = ausfuehren(D.dateien, D.schritte, empfohlen);
  assert.ok(r.dateien.includes(`Prüfen/${dup}`));
  assert.ok(!r.dateien.includes(dup));
  const neu = r.dateien.filter((d) => !d.startsWith('Prüfen/')).length + 1; // + Duplikat in Prüfen/
  assert.equal(neu, D.dateien.length + 1); // + Übersicht
});

test('mit allen Rechten ist das Duplikat weg', () => {
  const r = ausfuehren(D.dateien, D.schritte, alle);
  assert.ok(!r.dateien.some((d) => d.endsWith(dup)));
  assert.equal(r.dateien.length, D.dateien.length); // eine weg, eine (Übersicht) dazu
});

test('ohne Verschieben und Löschen wird das Duplikat nur gemeldet, Namen bleiben', () => {
  const r = ausfuehren(D.dateien, D.schritte, new Set(['lesen', 'anlegen']));
  assert.ok(r.dateien.includes(dup));
  for (const d of D.dateien) assert.ok(r.dateien.includes(d), d);
});

test('die Übersicht entsteht nur mit Anlegerecht und rechnet richtig', () => {
  const s = D.schritte.find((x) => x.art === 'anlegen');
  assert.ok(ausfuehren(D.dateien, D.schritte, empfohlen).dateien.includes(s.datei));
  assert.ok(!ausfuehren(D.dateien, D.schritte, new Set(['lesen', 'verschieben'])).dateien.includes(s.datei));
  const summe = D.belege.reduce((a, b) => a + b.cent, 0);
  assert.equal(summe, D.summeCent);
});

test('jeder umbenannte Beleg trägt Datum, Art und Betrag aus den Belegdaten', () => {
  const um = D.schritte.find((x) => x.art === 'umbenennen');
  assert.equal(um.paare.length, D.belege.length);
  for (const [, neu] of um.paare) assert.ok(D.belege.some((b) => neu.startsWith(`${b.datum}_${b.art}_`)), neu);
});
