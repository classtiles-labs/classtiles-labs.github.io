import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {daten, REPO} from './hilfen.mjs';

const D = daten('app-rundgang');

test('genau die Apps ChatGPT und Claude (Stefan, 04.11.2026: kein Gemini-Konto)', () => {
  assert.deepEqual(D.apps.map((a) => a.name), ['ChatGPT', 'Claude']);
});

test('jedes Bild liegt vor, ist klein genug und hat alt, Stand und Markierungen im Bild', () => {
  for (const app of D.apps) {
    assert.ok(app.bilder.length >= 3, app.name);
    for (const b of app.bilder) {
      assert.match(b.datei, /^assets\/kurs\/bilder\/[a-z0-9-]+\.webp$/);
      const pfad = path.join(REPO, b.datei);
      assert.ok(fs.existsSync(pfad), b.datei);
      assert.ok(fs.statSync(pfad).size <= 120 * 1024, `${b.datei} ist größer als 120 KB`);
      assert.ok(b.alt.length > 15, b.datei);
      assert.match(b.stand, /^(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember) \d{4}$/);
      assert.ok(b.titel, b.datei);
      for (const m of b.markierungen) {
        assert.ok(m.x >= 0 && m.x <= 1 && m.y >= 0 && m.y <= 1, `${b.datei}: Markierung außerhalb`);
        assert.ok(m.text, b.datei);
      }
    }
  }
});
