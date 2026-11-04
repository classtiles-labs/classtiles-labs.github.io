import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {daten, REPO} from './hilfen.mjs';

const D = daten('coding-agent');

test('Ablauf mit steigenden Zeitstempeln, endet bei einer Datei, die es gibt', () => {
  assert.ok(D.schritte.length >= 5);
  for (let i = 1; i < D.schritte.length; i++) assert.ok(D.schritte[i].zeit > D.schritte[i - 1].zeit);
  for (const s of D.schritte) assert.ok(['du', 'agent', 'befehl', 'datei', 'frage', 'fertig'].includes(s.art), s.art);
  const ende = D.schritte.at(-1);
  assert.equal(ende.art, 'fertig');
  assert.ok(fs.existsSync(path.join(REPO, D.ergebnis.datei)), D.ergebnis.datei);
  assert.ok(D.schritte.some((s) => s.art === 'frage'), 'mindestens eine Rückfrage um Erlaubnis');
});

test('Vergleich: Claude Code und Codex, jede Zeile belegt', () => {
  assert.deepEqual(D.vergleich.spalten, ['Claude Code', 'Codex']);
  for (const z of D.vergleich.zeilen) assert.equal(z.werte.length, 2, z.merkmal);
  assert.match(D.hinweis, /nachgestellt/i);
});
