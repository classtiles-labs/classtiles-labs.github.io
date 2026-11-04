import {test} from 'node:test';
import assert from 'node:assert/strict';
import {kopiere} from '../../../assets/kurs/ticket.js';

test('Zwischenablage da → kopiert', async () => {
  let drin = null;
  assert.equal(await kopiere('Hallo', {writeText: async (t) => { drin = t; }}), 'kopiert');
  assert.equal(drin, 'Hallo');
});

test('keine Zwischenablage → markieren (Review Focus 5)', async () => {
  assert.equal(await kopiere('Hallo', undefined), 'markieren');
  assert.equal(await kopiere('Hallo', {}), 'markieren');
});

test('Zwischenablage verweigert → markieren', async () => {
  assert.equal(await kopiere('Hallo', {writeText: async () => { throw new Error('nein'); }}), 'markieren');
});
