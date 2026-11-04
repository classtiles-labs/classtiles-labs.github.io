// Gemeinsame Hilfen der Node-Tests des KI-Kurses.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

export const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
export const netz = () => JSON.parse(fs.readFileSync(path.join(REPO, 'inhalt/kurs/netz.json'), 'utf8'));
export const ids = () => netz().stationen.map((s) => s.id);
export const daten = (name) => JSON.parse(fs.readFileSync(path.join(REPO, 'assets/kurs/daten', `${name}.json`), 'utf8'));
