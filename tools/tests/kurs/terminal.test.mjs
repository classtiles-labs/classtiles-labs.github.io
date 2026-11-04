import {test} from 'node:test';
import assert from 'node:assert/strict';
import {fuehreAus, startzustand} from '../../../assets/kurs/erlebnisse/terminal.js';

const lauf = (befehle) => {
  let z = startzustand();
  let aus = '';
  for (const b of befehle) ({ausgabe: aus, zustand: z} = fuehreAus(b, z));
  return {aus, z};
};

test('pwd zeigt den Heimordner', () => assert.equal(lauf(['pwd']).aus, '/Users/lehrkraft'));

test('cd in einen Ordner und zurück', () => {
  assert.equal(lauf(['cd unterricht', 'pwd']).aus, '/Users/lehrkraft/unterricht');
  assert.equal(lauf(['cd unterricht', 'cd ..', 'pwd']).aus, '/Users/lehrkraft');
  assert.equal(lauf(['cd ..', 'cd ..', 'cd ..', 'pwd']).aus, '/');
  assert.match(lauf(['cd gibtsnicht']).aus, /gibt es hier nicht/);
});

test('ls listet, mkdir legt an', () => {
  assert.match(lauf(['ls']).aus, /unterricht/);
  assert.match(lauf(['mkdir klasse-7b', 'ls']).aus, /klasse-7b/);
  assert.equal(lauf(['mkdir klasse-7b', 'cd klasse-7b', 'pwd']).aus, '/Users/lehrkraft/klasse-7b');
});

test('cat und echo', () => {
  assert.match(lauf(['cd unterricht', 'cat notiz.txt']).aus, /\S/);
  assert.match(lauf(['cat gibtsnicht.txt']).aus, /gibt es hier nicht/);
  assert.equal(lauf(['echo Hallo Klasse']).aus, 'Hallo Klasse');
});

test('help, unbekannt, leer, claude, codex, clear', () => {
  assert.match(lauf(['help']).aus, /pwd/);
  assert.equal(lauf(['tanz']).aus, 'Befehl nicht gefunden: tanz. Tippe help.');
  assert.equal(lauf(['']).aus, '');
  assert.equal(lauf(['   ']).aus, '');
  assert.match(lauf(['claude']).aus, /Nachbau/);
  assert.match(lauf(['codex']).aus, /Nachbau/);
  assert.equal(lauf(['clear']).z.leeren, true);
});
