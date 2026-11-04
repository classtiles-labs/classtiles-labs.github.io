import {test} from 'node:test';
import assert from 'node:assert/strict';
import {erstelleSpeicher, SCHLUESSEL} from '../../../assets/kurs/speicher.js';
import {ids} from './hilfen.mjs';

const IDS = ids();
const stand = {linie: 'E', start: 'wie-ki-schreibt', besucht: ['wie-ki-schreibt']};

function attrappe() {
  const daten = new Map();
  const zaehler = {get: 0, set: 0, remove: 0};
  return {
    zaehler, daten,
    getItem: (k) => { zaehler.get++; return daten.has(k) ? daten.get(k) : null; },
    setItem: (k, v) => { zaehler.set++; daten.set(k, String(v)); },
    removeItem: (k) => { zaehler.remove++; daten.delete(k); },
  };
}

test('der Schlüssel heißt classtiles-kurs', () => assert.equal(SCHLUESSEL, 'classtiles-kurs'));

test('ohne Zustimmung wird nichts geschrieben', () => {
  const a = attrappe();
  const sp = erstelleSpeicher(a);
  assert.equal(sp.istGemerkt(), false);
  sp.aktualisiere(stand);
  sp.aktualisiere(stand);
  assert.equal(a.zaehler.set, 0);
  assert.equal(sp.lade(IDS), null);
});

test('nach merke wird geschrieben und aktualisiert', () => {
  const a = attrappe();
  const sp = erstelleSpeicher(a);
  assert.equal(sp.merke(stand), true);
  assert.equal(a.daten.get('classtiles-kurs'), '1~E~wie-ki-schreibt~wie-ki-schreibt');
  sp.aktualisiere({...stand, besucht: ['wie-ki-schreibt', 'die-apps']});
  assert.equal(a.daten.get('classtiles-kurs'), '1~E~wie-ki-schreibt~wie-ki-schreibt,die-apps');
  assert.deepEqual(erstelleSpeicher(a).lade(IDS).besucht, ['wie-ki-schreibt', 'die-apps']);
});

test('vergiss löscht den Schlüssel und beendet das Mitschreiben', () => {
  const a = attrappe();
  const sp = erstelleSpeicher(a);
  sp.merke(stand);
  sp.vergiss();
  assert.equal(a.daten.has('classtiles-kurs'), false);
  sp.aktualisiere(stand);
  assert.equal(a.daten.has('classtiles-kurs'), false);
});

test('werfender Speicher bricht nichts (Review Focus 2)', () => {
  const kaputt = {getItem() { throw new Error('gesperrt'); }, setItem() { throw new Error('gesperrt'); }, removeItem() { throw new Error('gesperrt'); }};
  const sp = erstelleSpeicher(kaputt);
  assert.equal(sp.istGemerkt(), false);
  assert.equal(sp.merke(stand), false);
  assert.doesNotThrow(() => { sp.aktualisiere(stand); sp.vergiss(); });
  assert.equal(sp.lade(IDS), null);
});

test('kein Speicher vorhanden', () => {
  const sp = erstelleSpeicher(null);
  assert.equal(sp.istGemerkt(), false);
  assert.equal(sp.merke(stand), false);
  assert.equal(sp.lade(IDS), null);
});

test('gemerkter Müll wird ignoriert', () => {
  const a = attrappe();
  a.daten.set('classtiles-kurs', 'Unsinn');
  assert.equal(erstelleSpeicher(a).lade(IDS), null);
});
