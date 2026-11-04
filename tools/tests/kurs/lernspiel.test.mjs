import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {daten, REPO} from './hilfen.mjs';

const D = daten('lernspiel');

test('mindestens zwei Spiele aus echten Läufen', () => {
  assert.ok(D.spiele.length >= 2);
  for (const s of D.spiele) for (const k of ['titel', 'fach', 'klasse', 'datei', 'prompt', 'app', 'modell', 'datum']) assert.ok(s[k], `${s.titel}: ${k}`);
});

test('jedes Spiel liegt vor, hat einen Titel und lädt nichts von fremden Servern', () => {
  for (const s of D.spiele) {
    assert.match(s.datei, /^assets\/kurs\/spiele\/[a-z0-9-]+\.html$/);
    const html = fs.readFileSync(path.join(REPO, s.datei), 'utf8');
    assert.match(html, /<title>[^<]+<\/title>/);
    assert.doesNotMatch(html, /<(script|link|img|iframe|source)[^>]+(src|href)="https?:/i, `${s.datei}: Fremdressource`);
    assert.doesNotMatch(html, /\bfetch\s*\(|XMLHttpRequest|@import\s+url\(\s*['"]?https?:/i, `${s.datei}: Netzzugriff`);
  }
});
