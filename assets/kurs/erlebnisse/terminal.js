// Erlebnis „Das Terminal“: ein nachgebautes Terminal im Browser. Nichts davon berührt den
// echten Rechner — Ordner und Dateien sind ein kleines Spielzeug-Dateisystem im Speicher.

// Alles, was das Terminal braucht, steht hier; es gibt keine Datendatei.
export const DATEN = false;

const HEIM = ['Users', 'lehrkraft'];

export function startzustand() {
  return {
    pfad: [...HEIM],
    leeren: false,
    baum: {Users: {lehrkraft: {
      unterricht: {
        'notiz.txt': 'Montag: Klassenarbeit 7b zurückgeben.\nDienstag: Elternabend um 19 Uhr.',
        'arbeitsblatt-brueche.docx': '(Word-Datei, im Terminal nicht lesbar)',
      },
      Downloads: {},
      Schreibtisch: {'einkaufsliste.txt': 'Kreide, Folien, Kaffee'},
    }}},
  };
}

const HILFE = [
  'pwd            zeigt, in welchem Ordner du bist',
  'ls             listet, was im Ordner liegt',
  'cd ordner      wechselt in einen Ordner (cd .. geht eine Ebene zurück)',
  'mkdir name     legt einen Ordner an',
  'cat datei      zeigt den Inhalt einer Textdatei',
  'echo text      gibt Text aus',
  'clear          leert das Fenster',
  'claude, codex  so startest du in echt einen Coding-Agenten',
].join('\n');

const ordner = (baum, pfad) => pfad.reduce((o, teil) => o?.[teil], baum);

export function fuehreAus(eingabe, zustand) {
  const z = {...zustand, leeren: false};
  const [befehl, ...rest] = eingabe.trim().split(/\s+/);
  const arg = rest.join(' ');
  if (!befehl) return {ausgabe: '', zustand: z};
  const hier = ordner(z.baum, z.pfad);
  switch (befehl) {
    case 'help':
      return {ausgabe: HILFE, zustand: z};
    case 'pwd':
      return {ausgabe: '/' + z.pfad.join('/'), zustand: z};
    case 'ls':
      return {ausgabe: Object.keys(hier).sort().map((n) => (typeof hier[n] === 'object' ? `${n}/` : n)).join('   '), zustand: z};
    case 'cd': {
      if (!arg || arg === '~') return {ausgabe: '', zustand: {...z, pfad: [...HEIM]}};
      if (arg === '..') return {ausgabe: '', zustand: {...z, pfad: z.pfad.slice(0, -1)}};
      if (typeof hier[arg] === 'object') return {ausgabe: '', zustand: {...z, pfad: [...z.pfad, arg]}};
      return {ausgabe: `cd: ${arg} gibt es hier nicht.`, zustand: z};
    }
    case 'mkdir': {
      if (!/^[\w.-]+$/.test(arg)) return {ausgabe: 'mkdir: Bitte einen Namen ohne Leerzeichen angeben, z. B. mkdir klasse-7b', zustand: z};
      if (arg in hier) return {ausgabe: `mkdir: ${arg} gibt es schon.`, zustand: z};
      const baum = structuredClone(z.baum);
      ordner(baum, z.pfad)[arg] = {};
      return {ausgabe: '', zustand: {...z, baum}};
    }
    case 'cat': {
      if (!(arg in hier)) return {ausgabe: `cat: ${arg || '(nichts)'} gibt es hier nicht.`, zustand: z};
      if (typeof hier[arg] === 'object') return {ausgabe: `cat: ${arg} ist ein Ordner.`, zustand: z};
      return {ausgabe: hier[arg], zustand: z};
    }
    case 'echo':
      return {ausgabe: arg, zustand: z};
    case 'clear':
      return {ausgabe: '', zustand: {...z, leeren: true}};
    case 'claude':
    case 'codex':
      return {
        ausgabe: `Hier läuft nur ein Nachbau. In einem echten Terminal startet „${befehl}“ den Coding-Agenten im aktuellen Ordner. Dann schreibst du ihm in normalen Sätzen, was er bauen soll, und er fragt, bevor er etwas Wichtiges tut.`,
        zustand: z,
      };
    default:
      return {ausgabe: `Befehl nicht gefunden: ${befehl}. Tippe help.`, zustand: z};
  }
}

export function mount(el) {
  let z = startzustand();
  const verlauf = [];
  let zeiger = 0;
  let geschafft = false;
  const prompt = () => `lehrkraft ${z.pfad.length > 2 ? z.pfad.at(-1) : z.pfad.length === 2 ? '~' : '/' + z.pfad.join('/')} %`;
  el.innerHTML = `
    <h2>Das Terminal</h2>
    <p class="tm-anleitung"><b>Aufgabe:</b> Leg einen Ordner für eine Klasse an und wechsle hinein. Tipp: Fang mit <code>help</code> an.</p>
    <div class="tm-fenster">
      <div class="tm-leiste" aria-hidden="true"><i></i><i></i><i></i><span>Terminal (Nachbau)</span></div>
      <pre class="tm-ausgabe" aria-live="polite">Willkommen. Das hier ist ein Nachbau, dein Rechner bleibt unberührt.\n</pre>
      <form class="tm-zeile"><label><span class="tm-prompt"></span><input type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Befehl eingeben"></label></form>
    </div>
    <div class="tm-tasten" aria-label="Schnelltasten">${['help', 'pwd', 'ls', 'cd unterricht', 'cat notiz.txt', 'cd ..', 'mkdir klasse-7b', 'cd klasse-7b'].map((b) => `<button type="button" data-befehl="${b}">${b}</button>`).join('')}</div>
    <p class="tm-geschafft" hidden></p>`;
  const aus = el.querySelector('.tm-ausgabe');
  const feld = el.querySelector('input');
  const zeige = () => { el.querySelector('.tm-prompt').textContent = prompt() + ' '; };
  function los(befehl) {
    const vorher = prompt();
    const r = fuehreAus(befehl, z);
    z = r.zustand;
    if (befehl.trim()) { verlauf.push(befehl); zeiger = verlauf.length; }
    aus.textContent = z.leeren ? '' : `${aus.textContent}${vorher} ${befehl}\n${r.ausgabe ? r.ausgabe + '\n' : ''}`;
    aus.scrollTop = aus.scrollHeight;
    zeige();
    // Geschafft: Der aktuelle Ordner wurde in dieser Sitzung angelegt.
    const neu = z.pfad.length > 2 && !(z.pfad.at(-1) in (startzustand().baum.Users.lehrkraft));
    if (!geschafft && neu) {
      geschafft = true;
      const g = el.querySelector('.tm-geschafft');
      g.innerHTML = `<b>Geschafft.</b> Du hast einen Ordner angelegt und bist hineingewechselt. Genau hier würdest du in echt <code>claude</code> oder <code>codex</code> starten: Der Agent arbeitet dann in diesem Ordner.`;
      g.hidden = false;
    }
  }
  el.querySelector('form').addEventListener('submit', (ev) => { ev.preventDefault(); los(feld.value); feld.value = ''; });
  feld.addEventListener('keydown', (ev) => {
    if (ev.key === 'ArrowUp' && zeiger > 0) { zeiger--; feld.value = verlauf[zeiger]; ev.preventDefault(); }
    if (ev.key === 'ArrowDown' && zeiger < verlauf.length) { zeiger++; feld.value = verlauf[zeiger] ?? ''; ev.preventDefault(); }
  });
  el.querySelector('.tm-tasten').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-befehl]');
    if (b) los(b.dataset.befehl);
  });
  zeige();
}
