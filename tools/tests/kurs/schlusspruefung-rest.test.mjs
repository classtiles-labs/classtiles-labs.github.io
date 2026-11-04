// Befunde der Schlussprüfung zu den sieben neuen Stationen (04.11.2026), je ein Test.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {REPO, daten} from './hilfen.mjs';
import {EINSTELLUNG_HINWEIS} from '../../../assets/kurs/erlebnisse/statusline-baukasten.js';
import {checkZeilen} from '../../../assets/kurs/erlebnisse/feedback-check.js';

const lies = (p) => fs.readFileSync(path.join(REPO, p), 'utf8');

test('Fund 2: der settings.json-Eintrag warnt vor dem Überschreiben einer bestehenden Datei', () => {
  assert.match(EINSTELLUNG_HINWEIS, /schon/);
  assert.match(EINSTELLUNG_HINWEIS, /statusLine/);
});

test('Fund 7: der Feedback-Check zählt nächste Schritte, nicht „Baustellen“', () => {
  const [eins, zwei] = daten('feedback-check').laeufe;
  const namen = checkZeilen(eins).map(([n]) => n);
  assert.ok(!namen.includes('Baustellen'));
  const zeile = (l) => checkZeilen(l).find(([n]) => n === 'Nächste Schritte');
  assert.match(zeile(eins)[1], /^5\b/);
  assert.match(zeile(zwei)[1], /^1\b/);
});

test('Fund 8: kein „rechts“ als Ortsangabe, die am Handy nicht stimmt', () => {
  for (const p of ['inhalt/kurs/stationen/workflows.html', 'assets/kurs/erlebnisse/workflow-baukasten.js', 'assets/kurs/erlebnisse/feedback-check.js']) {
    assert.doesNotMatch(lies(p), /[Rr]echts (prüft|daneben)/, p);
  }
});

test('Fund 9: der Betrieb auf Servern des Anbieters ist nur für Cowork belegt und nur dort gesagt', () => {
  const t = lies('inhalt/kurs/stationen/agent-im-ordner.html').replace(/\s+/g, ' ');
  const satz = t.split(/(?<=\.) /).find((s) => /Servern/.test(s));
  assert.match(satz, /Cowork/);
  assert.doesNotMatch(satz, /ChatGPT/);
});
