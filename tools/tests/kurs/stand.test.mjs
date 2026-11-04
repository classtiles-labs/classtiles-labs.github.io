import {test} from 'node:test';
import assert from 'node:assert/strict';
import {leererStand, besuche, kodiere, dekodiere, ausFragment, alsFragment} from '../../../assets/kurs/stand.js';
import {ids} from './hilfen.mjs';

const IDS = ids();

test('leerer Stand', () => {
  assert.deepEqual(leererStand(), {linie: null, start: null, besucht: []});
  assert.equal(kodiere(leererStand()), '1~-~-~');
});

test('besuche hängt an, ohne Duplikate, Reihenfolge bleibt', () => {
  let s = besuche(leererStand(), 'wie-ki-schreibt');
  s = besuche(s, 'die-apps');
  s = besuche(s, 'wie-ki-schreibt');
  assert.deepEqual(s.besucht, ['wie-ki-schreibt', 'die-apps']);
});

test('kodiere nach festem Format', () => {
  assert.equal(kodiere({linie: 'E', start: 'wie-ki-schreibt', besucht: ['wie-ki-schreibt', 'die-apps']}),
    '1~E~wie-ki-schreibt~wie-ki-schreibt,die-apps');
});

test('Rundreise', () => {
  const s = {linie: 'A', start: 'eigenes-material', besucht: ['eigenes-material', 'gut-fragen']};
  assert.deepEqual(dekodiere(kodiere(s), IDS), s);
});

test('fremde Version und Müll werden ignoriert (Review Focus 1)', () => {
  assert.equal(dekodiere('2~E~x~y', IDS), null);
  assert.equal(dekodiere('%%%', IDS), null);
  assert.equal(dekodiere('', IDS), null);
  assert.equal(dekodiere(undefined, IDS), null);
  assert.equal(dekodiere('1~E~wie-ki-schreibt', IDS), null);
});

test('unbekannte Kennungen werden herausgefiltert', () => {
  assert.deepEqual(dekodiere('1~E~wie-ki-schreibt~wie-ki-schreibt,gibtsnicht', IDS).besucht, ['wie-ki-schreibt']);
  const s = dekodiere('1~Z~gibtsnicht~', IDS);
  assert.equal(s.linie, null);
  assert.equal(s.start, null);
  assert.deepEqual(s.besucht, []);
});

test('Fragment hin und zurück', () => {
  const s = {linie: 'B', start: 'terminal', besucht: ['terminal']};
  assert.equal(alsFragment(s), '#stand=1~B~terminal~terminal');
  assert.deepEqual(ausFragment('#stand=1~B~terminal~terminal', IDS), s);
  assert.deepEqual(ausFragment('#stand=1%7EB%7Eterminal%7Eterminal', IDS), s);
  assert.equal(ausFragment('#fahrkarte', IDS), null);
  assert.equal(ausFragment('#stand=%E0%A4%A', IDS), null);
});
