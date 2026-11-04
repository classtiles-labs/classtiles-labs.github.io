import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fortschritt} from '../../../assets/kurs/erlebnisse/werkstatt.js';
import {daten, REPO} from './hilfen.mjs';

const D = daten('werkstatt');

test('fortschritt nennt geprüfte Punkte und meldet, wenn alles geprüft ist', () => {
  assert.equal(fortschritt(new Set([0, 2]), 5), '2 von 5 geprüft');
  assert.equal(fortschritt(new Set([0, 1, 2]), 3), 'Alle 3 Punkte geprüft');
});

test('drei echte Schritte: Plan, Bau, Nachbessern', () => {
  assert.deepEqual(D.schritte.map((s) => s.id), ['plan', 'bau', 'nachbessern']);
  for (const s of D.schritte) for (const k of ['titel', 'prompt', 'antwort', 'kommentar', 'sekunden']) assert.ok(s[k], `${s.id}.${k}`);
  for (const k of ['app', 'version', 'modell', 'datum', 'modus']) assert.ok(D.lauf[k], k);
});

test('Bau und Nachbessern verweisen auf echte Werkzeugdateien ohne Fremdressourcen', () => {
  for (const s of D.schritte.filter((x) => x.datei)) {
    assert.match(s.datei, /^assets\/kurs\/werkzeuge\/[a-z0-9-]+\.html$/);
    const html = fs.readFileSync(path.join(REPO, s.datei), 'utf8');
    assert.match(html, /<title>[^<]+<\/title>/);
    assert.doesNotMatch(html, /<(script|link|img|iframe|source)[^>]+(src|href)="https?:/i, s.datei);
    assert.doesNotMatch(html, /\bfetch\s*\(|XMLHttpRequest/i, s.datei);
  }
  assert.equal(D.schritte.filter((x) => x.datei).length, 2);
});

test('die zweite Fassung hat den gewünschten Arbeitsauftrag, die erste nicht', () => {
  const [v1, v2] = D.schritte.filter((x) => x.datei).map((s) => fs.readFileSync(path.join(REPO, s.datei), 'utf8'));
  assert.ok(!v1.includes('Arbeitsauftrag'));
  assert.ok(v2.includes('Arbeitsauftrag'));
});

test('die Prüfliste hat mindestens vier Punkte', () => {
  assert.ok(D.pruefliste.length >= 4);
});
