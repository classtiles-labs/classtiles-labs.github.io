import {test} from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {vorschau, skript, EINSTELLUNG, REIHENFOLGE} from '../../../assets/kurs/erlebnisse/statusline-baukasten.js';
import {daten} from './hilfen.mjs';

const D = daten('statusline-baukasten');
const B = D.beispiel;

test('Vorschau in fester Reihenfolge, egal in welcher Folge gewählt', () => {
  assert.equal(vorschau(['modell', 'ordner', 'kontext'], B), 'Opus | unterricht | Kontext 8 %');
  assert.equal(vorschau(['kontext', 'modell'], B), 'Opus | Kontext 8 %');
  assert.equal(vorschau([], B), '');
});

test('Kosten werden auf Cent gerundet und mit Komma geschrieben', () => {
  assert.equal(vorschau(['kosten'], B), '0,01 $');
  assert.equal(vorschau(['kosten'], {...B, cost: {total_cost_usd: 1.5}}), '1,50 $');
});

test('fehlende Werte fallen weg statt „null“ zu zeigen', () => {
  const ohne = {...B, rate_limits: undefined, effort: undefined};
  assert.equal(vorschau(['modell', 'woche', 'denkstufe'], ohne), 'Opus');
  assert.equal(vorschau(['kontext'], {...B, context_window: {used_percentage: null}}), 'Kontext 0 %');
});

test('das Skript liest nur die gewählten Felder', () => {
  const s = skript(['modell']);
  assert.ok(s.startsWith('#!/bin/bash\n'));
  assert.ok(s.includes('.model.display_name'));
  assert.ok(!s.includes('total_cost_usd'));
});

test('die Einstellung ist gültiges JSON für einen Befehl', () => {
  const e = JSON.parse(EINSTELLUNG);
  assert.equal(e.statusLine.type, 'command');
  assert.equal(e.statusLine.command, '~/.claude/statusline.sh');
});

const jq = spawnSync('jq', ['--version']).status === 0;
test('das Skript gibt mit bash und jq genau die Vorschau aus', {skip: !jq && 'jq fehlt'}, () => {
  const faelle = [REIHENFOLGE, ['modell', 'ordner', 'kontext'], ['kosten', 'woche'], ['denkstufe'], []];
  for (const auswahl of faelle) {
    for (const eingabe of [B, {...B, rate_limits: undefined, cost: {total_cost_usd: 1.5}}]) {
      const r = spawnSync('bash', ['-c', skript(auswahl)], {input: JSON.stringify(eingabe), encoding: 'utf8'});
      assert.equal(r.status, 0, r.stderr);
      assert.equal(r.stdout.replace(/\n$/, ''), vorschau(auswahl, eingabe), auswahl.join(','));
    }
  }
});

test('jeder Baustein der Daten ist bekannt', () => {
  assert.deepEqual(D.bausteine.map((b) => b.id), REIHENFOLGE);
});
