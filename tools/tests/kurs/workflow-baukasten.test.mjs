import {test} from 'node:test';
import assert from 'node:assert/strict';
import {pruefe, alsSkill, verschiebe} from '../../../assets/kurs/erlebnisse/workflow-baukasten.js';
import {daten} from './hilfen.mjs';

const D = daten('workflow-baukasten');
const richtig = ['material', 'plan', 'blatt', 'loesung', 'pruefen', 'ablegen'];

test('die richtige Reihenfolge erfüllt alle Regeln', () => {
  assert.ok(pruefe(richtig, D.regeln).every((r) => r.ok));
});

test('Plan nach dem Arbeitsblatt verletzt die Freigabe-Regel', () => {
  const r = pruefe(['material', 'blatt', 'plan', 'loesung', 'pruefen', 'ablegen'], D.regeln);
  const freigabe = r.find((x) => x.text.includes('Freigabe'));
  assert.equal(freigabe.ok, false);
});

test('die Startreihenfolge ist gemischt und enthält jeden Schritt genau einmal', () => {
  assert.deepEqual([...D.start].sort(), [...richtig].sort());
  assert.ok(pruefe(D.start, D.regeln).some((r) => !r.ok));
});

test('verschiebe tauscht mit dem Nachbarn und bleibt an den Rändern stehen', () => {
  assert.deepEqual(verschiebe(['a', 'b', 'c'], 1, -1), ['b', 'a', 'c']);
  assert.deepEqual(verschiebe(['a', 'b', 'c'], 0, -1), ['a', 'b', 'c']);
  assert.deepEqual(verschiebe(['a', 'b', 'c'], 2, 1), ['a', 'b', 'c']);
});

test('alsSkill schreibt Frontmatter mit name und description und nummeriert in der Reihenfolge', () => {
  const md = alsSkill(D.kopf, richtig, D.schritte);
  assert.ok(md.startsWith(`---\nname: ${D.kopf.name}\ndescription: `));
  assert.match(D.kopf.name, /^[a-z0-9-]+$/);
  const zeilen = md.split('\n').filter((z) => /^\d+\. /.test(z));
  assert.equal(zeilen.length, richtig.length);
  richtig.forEach((id, i) => assert.ok(zeilen[i].startsWith(`${i + 1}. ${D.schritte[id]}`), id));
});

test('die Beschreibung bleibt gültiges YAML ohne Anführungszeichen', () => {
  assert.doesNotMatch(D.kopf.beschreibung, /: |#|^[\s'"\[{>|*&!%@`-]/);
});
