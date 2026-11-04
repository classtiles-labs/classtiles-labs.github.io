import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {startzustand, belegt, fuehreAus, kontextZeilen, anzeigeText} from '../../../assets/kurs/erlebnisse/kontext-terminal.js';
import {daten, REPO} from './hilfen.mjs';

const D = daten('kontext-terminal');
const lauf = (werkzeug, eingaben) => eingaben.reduce((z, e) => fuehreAus(e, z, D).zustand, startzustand(werkzeug));
const grund = (w) => Object.values(D.werkzeuge[w].grundlast).reduce((a, b) => a + b, 0);

test('beide Werkzeuge: Claude Code und Codex', () => {
  assert.deepEqual(Object.keys(D.werkzeuge), ['claude', 'codex']);
});

test('zu Beginn ist nur die Grundlast belegt, Arbeit füllt den Kontext', () => {
  for (const w of ['claude', 'codex']) {
    assert.equal(belegt(startzustand(w), D), grund(w));
    const z = lauf(w, ['Auftrag eins', 'Auftrag zwei']);
    assert.ok(belegt(z, D) > grund(w));
  }
});

test('der Kontext läuft nie über 100 % und fasst automatisch zusammen', () => {
  for (const w of ['claude', 'codex']) {
    let z = startzustand(w);
    let auto = false;
    for (let i = 0; i < 30; i++) {
      const r = fuehreAus('weiter', z, D);
      z = r.zustand;
      assert.ok(belegt(z, D) <= 100);
      if (r.ausgabe.includes(D.werkzeuge[w].texte.autoCompact)) auto = true;
    }
    assert.ok(auto, `${w}: kein automatisches Zusammenfassen`);
  }
});

test('/compact verkleinert das Gespräch auf die Zusammenfassung, aber nicht auf null', () => {
  const z = lauf('claude', ['a', 'b', 'c']);
  const r = fuehreAus('/compact', z, D);
  assert.equal(r.zustand.gespraech, D.zusammenfassung);
  assert.ok(belegt(r.zustand, D) < belegt(z, D));
  assert.ok(r.zustand.gespraech > 0);
  assert.match(fuehreAus('/compact behalte die Aufgaben', z, D).ausgabe.join('\n'), /behalte die Aufgaben/);
  assert.equal(fuehreAus('/compact', startzustand('claude'), D).ausgabe[0], D.werkzeuge.claude.befehle['/compact'].leer);
});

test('neu anfangen leert das Gespräch: /clear und /new in beiden Werkzeugen', () => {
  for (const [w, befehl] of [['claude', '/clear'], ['claude', '/new'], ['codex', '/new'], ['codex', '/clear']]) {
    const z = lauf(w, ['a', 'b', befehl]);
    assert.equal(z.gespraech, 0, `${w} ${befehl}`);
    assert.equal(belegt(z, D), grund(w));
  }
});

test('nur in Claude Code (belegt) steht der alte Chat nach /clear in /resume', () => {
  const liste = (w, b) => fuehreAus('/resume', lauf(w, ['a', 'b', b]), D).ausgabe.join('\n');
  assert.ok(liste('claude', '/clear').includes(D.arbeit[0].thema));
  assert.ok(!liste('codex', '/new').includes(D.arbeit[0].thema));
});

test('/compact in Codex nimmt keine Anweisung an und sagt das', () => {
  const z = lauf('codex', ['a', 'b', 'c']);
  const r = fuehreAus('/compact bitte kurz', z, D).ausgabe.join('\n');
  assert.ok(r.includes(D.werkzeuge.codex.befehle['/compact'].ohneAnweisung));
});

test('/context zeigt jede Kategorie, die Prozente ergeben 100', () => {
  const z = lauf('claude', ['a', 'b']);
  const zeilen = kontextZeilen(z, D);
  const prozente = zeilen.map((l) => Number(l.match(/(\d+) %$/)[1]));
  assert.equal(prozente.reduce((a, b) => a + b, 0), 100);
  for (const k of Object.keys(D.werkzeuge.claude.grundlast)) assert.ok(zeilen.some((l) => l.startsWith(k)), k);
});

test('Befehle des anderen Werkzeugs bekommen einen Hinweis statt einer Fehlermeldung', () => {
  for (const [w, fremd] of [['codex', '/context'], ['codex', '/help'], ['codex', '/rewind'], ['codex', '/memory']]) {
    assert.ok(!D.werkzeuge[w].befehle[fremd], `${w} ${fremd} sollte fehlen`);
    const r = fuehreAus(fremd, startzustand(w), D).ausgabe.join('\n');
    assert.equal(r, D.werkzeuge[w].fehlt[fremd], `${w} ${fremd}`);
  }
  assert.match(fuehreAus('/zaubern', startzustand('claude'), D).ausgabe[0], /\/zaubern/);
});

test('/help in Claude Code listet genau seine Befehle, jede Schnelltaste ist ein bekannter Befehl', () => {
  const hilfe = fuehreAus('/help', startzustand('claude'), D).ausgabe;
  assert.equal(hilfe.length, Object.keys(D.werkzeuge.claude.befehle).length);
  for (const w of ['claude', 'codex']) {
    for (const t of D.werkzeuge[w].tasten) assert.ok(D.werkzeuge[w].befehle[t.split(' ')[0]], `${w}: ${t}`);
  }
});

test('der Vergleich nennt für jeden Zweck beide Werkzeuge', () => {
  assert.ok(D.vergleich.length >= 6);
  for (const v of D.vergleich) assert.ok(v.zweck && v.claude && v.codex, v.zweck);
});

// Befunde der Prüfung vom 04.11.2026
test('Prüfung 1: /clear in Codex leert das Fenster, /new nicht', () => {
  const z = lauf('codex', ['a']);
  assert.equal(fuehreAus('/clear', z, D).leeren, true);
  assert.ok(!fuehreAus('/new', z, D).leeren);
});

test('Prüfung 2: der Spickzettel passt aufs Handy (höchstens 30 Zeichen je Zeile)', () => {
  const html = fs.readFileSync(path.join(REPO, 'inhalt/kurs/stationen/kontext-befehle.html'), 'utf8');
  const pre = html.match(/<pre class="ticket-prompt">([\s\S]*?)<\/pre>/)[1];
  for (const zeile of pre.split('\n')) assert.ok(zeile.length <= 30, `zu lang: ${zeile}`);
  assert.doesNotMatch(html, /[Ll]inks Claude Code/);
});

test('Prüfung 3: die Füllstandsanzeige sagt, woher sie in echt kommt', () => {
  assert.match(anzeigeText(startzustand('claude'), D), /Statusline/);
  assert.match(anzeigeText(startzustand('codex'), D), /übrig/);
});

test('Prüfung 4: „Geschafft“ zählt /compact nur, wenn wirklich zusammengefasst wurde', () => {
  assert.ok(!lauf('claude', ['/compact', '/clear']).benutzt.includes('compact'));
  assert.ok(lauf('claude', ['a', '/compact']).benutzt.includes('compact'));
});

test('Prüfung 6: Codex-/status zeigt die Limits als „übrig“ wie das echte Werkzeug', () => {
  const zeilen = fuehreAus('/status', startzustand('codex'), D).ausgabe.join('\n');
  assert.doesNotMatch(zeilen, /genutzt/);
  assert.match(zeilen, /Limit.*übrig/);
});

test('Prüfung 7: Codex-/resume sagt, dass die Doku zum eigenen Chat schweigt', () => {
  assert.match(D.werkzeuge.codex.befehle['/resume'].hinweis, /Doku/);
});

test('Prüfung 8: /init in Claude Code beschreibt nur die belegte Wirkung', () => {
  assert.doesNotMatch(D.werkzeuge.claude.befehle['/init'].zeilen.join(' '), /Sieht sich/);
});
