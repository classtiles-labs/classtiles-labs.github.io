import {test} from 'node:test';
import assert from 'node:assert/strict';
import {naechste} from '../../../assets/kurs/erlebnisse/superpowers-phasen.js';
import {daten} from './hilfen.mjs';

const D = daten('superpowers-phasen');
// Die 15 Skills von Superpowers 7.0 (github.com/obra/superpowers, Ordner skills/).
const SKILLS = ['brainstorming', 'diagnosing-superpowers', 'dispatching-parallel-agents', 'executing-plans',
  'finishing-a-development-branch', 'receiving-code-review', 'requesting-code-review', 'subagent-driven-development',
  'systematic-debugging', 'test-driven-development', 'using-git-worktrees', 'using-superpowers',
  'verification-before-completion', 'writing-plans', 'writing-skills'];

test('fünf Phasen in fester Reihenfolge', () => {
  assert.deepEqual(D.phasen.map((p) => p.id), ['fragen', 'entwurf', 'plan', 'bauen', 'pruefung']);
});

test('jede Phase nennt echte Skills und was ohne sie passiert', () => {
  for (const p of D.phasen) {
    assert.ok(p.skills.length >= 1, p.id);
    for (const s of p.skills) assert.ok(SKILLS.includes(s), `${p.id}: ${s}`);
    for (const k of ['titel', 'so', 'ohne']) assert.ok(p[k], `${p.id}.${k}`);
  }
  assert.ok(D.bilanz.zeilen.length >= 3);
});

test('das Erlebnis ist ein nachgestelltes Beispiel und sagt nichts über den Bau dieser Seite', () => {
  assert.ok(D.beispiel);
  assert.match(D.hinweis, /Beispiel, nachgestellt/);
  const alles = JSON.stringify(D);
  assert.doesNotMatch(alles, /dieser Kurs|dieses Kurses|diesen Kurs|Arbeitsprotokoll/);
});

test('naechste läuft bis zur letzten Phase und bleibt dort', () => {
  assert.equal(naechste(0, 5), 1);
  assert.equal(naechste(4, 5), 4);
});
