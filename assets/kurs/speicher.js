// Der einzige Ort der Website, der etwas auf dem Gerät ablegt — und erst, nachdem die
// Lehrkraft „Fortschritt auf diesem Gerät merken“ angetippt hat (Datenschutzerklärung, Abschnitt
// zum KI-Kurs). Gespeichert wird nur der kodierte Stand (welche Stationen besucht sind) unter
// einem Schlüssel. „Vergessen“ löscht ihn wieder.
//
// tools/tests/test_seo.py erlaubt Speicherzugriffe nur in dieser Datei und nur auf localStorage.
import {kodiere, dekodiere} from './stand.js';

export const SCHLUESSEL = 'classtiles-kurs';

// Schon das Lesen von window.localStorage kann werfen (gesperrte Website-Daten).
export function speicherDesBrowsers() {
  try {
    return globalThis.localStorage ?? null;
  } catch {
    return null;
  }
}

export function erstelleSpeicher(speicher) {
  const istGemerkt = () => {
    if (!speicher) return false;
    try {
      return speicher.getItem(SCHLUESSEL) !== null;
    } catch {
      return false;
    }
  };
  const schreibe = (stand) => {
    if (!speicher) return false;
    try {
      speicher.setItem(SCHLUESSEL, kodiere(stand));
      return true;
    } catch {
      return false;
    }
  };
  return {
    istGemerkt,
    lade(bekannteIds) {
      if (!istGemerkt()) return null;
      try {
        return dekodiere(speicher.getItem(SCHLUESSEL), bekannteIds);
      } catch {
        return null;
      }
    },
    merke: schreibe,
    aktualisiere(stand) {
      if (istGemerkt()) schreibe(stand);
    },
    vergiss() {
      if (!speicher) return;
      try {
        speicher.removeItem(SCHLUESSEL);
      } catch {
        // gesperrter Speicher: nichts zu löschen
      }
    },
  };
}
