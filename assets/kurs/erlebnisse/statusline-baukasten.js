// Erlebnis „Statusline“: Bausteine wählen, die Zeile unten in Claude Code live sehen und das
// fertige Skript samt Einstellung kopieren. Vorschau und Skript rechnen dieselben Werte.
import {kopiere} from '../ticket.js';

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export const REIHENFOLGE = ['modell', 'ordner', 'kontext', 'kosten', 'woche', 'denkstufe'];

const leer = (v) => v === undefined || v === null || v === '';
const cent = (usd) => Math.round((usd ?? 0) * 100);

// Je Baustein: Wert in der Vorschau (aus dem Beispiel-JSON) und dieselbe Rechnung als bash mit jq.
const BAUSTEINE = {
  modell: {
    wert: (j) => j.model?.display_name,
    bash: `M=$(echo "$input" | jq -r '.model.display_name // empty')\n[ -n "$M" ] && teile+=("$M")`,
  },
  ordner: {
    wert: (j) => j.workspace?.current_dir?.split('/').filter(Boolean).pop(),
    bash: `D=$(echo "$input" | jq -r '.workspace.current_dir // empty')\n[ -n "$D" ] && teile+=("\${D##*/}")`,
  },
  kontext: {
    wert: (j) => `Kontext ${Math.floor(j.context_window?.used_percentage ?? 0)} %`,
    bash: `K=$(echo "$input" | jq -r '.context_window.used_percentage // 0 | floor')\nteile+=("Kontext $K %")`,
  },
  kosten: {
    wert: (j) => { const c = cent(j.cost?.total_cost_usd); return `${Math.floor(c / 100)},${String(c % 100).padStart(2, '0')} $`; },
    bash: `C=$(echo "$input" | jq -r '(.cost.total_cost_usd // 0) * 100 | round')\nteile+=("$(printf '%d,%02d $' $((C / 100)) $((C % 100)))")`,
  },
  woche: {
    wert: (j) => { const w = j.rate_limits?.seven_day?.used_percentage; return leer(w) ? undefined : `Woche ${Math.floor(w)} %`; },
    bash: `W=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty | floor')\n[ -n "$W" ] && teile+=("Woche $W %")`,
  },
  denkstufe: {
    wert: (j) => j.effort?.level,
    bash: `S=$(echo "$input" | jq -r '.effort.level // empty')\n[ -n "$S" ] && teile+=("$S")`,
  },
};

const geordnet = (auswahl) => REIHENFOLGE.filter((id) => auswahl.includes(id));

export function vorschau(auswahl, json) {
  return geordnet(auswahl).map((id) => BAUSTEINE[id].wert(json)).filter((w) => !leer(w)).join(' | ');
}

export function skript(auswahl) {
  return [
    '#!/bin/bash',
    '# Statusline für Claude Code, gebaut im KI-Kurs auf classtiles.de. Braucht jq.',
    'input=$(cat)',
    'teile=()',
    ...geordnet(auswahl).map((id) => BAUSTEINE[id].bash),
    'zeile=""',
    'for t in "${teile[@]}"; do zeile="${zeile:+$zeile | }$t"; done',
    'echo "$zeile"',
    '',
  ].join('\n');
}

export const EINSTELLUNG = `{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  }
}`;

export const EINSTELLUNG_HINWEIS = 'Gibt es die Datei schon, ersetz sie nicht: Füg nur den Teil "statusLine": { … } innerhalb der äußeren geschweiften Klammern ein, mit einem Komma nach dem Eintrag davor.';

export function mount(el, daten) {
  if (!daten?.bausteine?.length) return;
  const auswahl = new Set(daten.start);
  el.innerHTML = `
    <h2>Deine Statusline</h2>
    <p class="sl-anleitung">Tipp an, was du unten in Claude Code immer sehen willst. Die Zeile darunter zeigt es mit Beispieldaten.</p>
    <div class="sl-bausteine">${daten.bausteine.map((b) => `<button type="button" class="pb-chip" data-b="${b.id}" aria-pressed="false">${esc(b.name)}</button>`).join('')}</div>
    <div class="sl-terminal" aria-live="polite"><span class="sl-eingabe">&gt; </span><span class="sl-zeile"></span></div>
    <p class="pb-label">1 · Skript, gespeichert als <code>~/.claude/statusline.sh</code></p>
    <pre class="pb-prompt sl-code" data-teil="skript"></pre>
    <p class="pb-label">2 · Im Terminal einmal ausführen</p>
    <pre class="pb-prompt sl-code">chmod +x ~/.claude/statusline.sh</pre>
    <p class="pb-label">3 · Eintrag in <code>~/.claude/settings.json</code></p>
    <pre class="pb-prompt sl-code" data-teil="einstellung"></pre>
    <p class="sl-hinweis">${esc(EINSTELLUNG_HINWEIS)}</p>
    <div class="sl-kopieren">
      <button type="button" class="btn b-line" data-kopiere="skript">Skript kopieren</button>
      <button type="button" class="btn b-line" data-kopiere="einstellung">Eintrag kopieren</button>
      <span class="sl-meldung" role="status"></span>
    </div>
    <p class="ew-hinweis">Beispieldaten in der Vorschau. ${esc(daten.stand)}. Das Skript braucht das Programm jq.</p>`;
  el.querySelector('[data-teil="einstellung"]').textContent = EINSTELLUNG;
  function zeichne() {
    el.querySelectorAll('[data-b]').forEach((b) => {
      const an = auswahl.has(b.dataset.b);
      b.classList.toggle('an', an);
      b.setAttribute('aria-pressed', String(an));
    });
    const zeile = vorschau([...auswahl], daten.beispiel);
    el.querySelector('.sl-zeile').textContent = (zeile || '(leer)').replace(/ (%|\$)/g, '\u00a0$1');
    el.querySelector('[data-teil="skript"]').textContent = skript([...auswahl]);
    el.querySelector('.sl-meldung').textContent = '';
  }
  el.querySelector('.sl-bausteine').addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-b]');
    if (!b) return;
    if (auswahl.has(b.dataset.b)) auswahl.delete(b.dataset.b); else auswahl.add(b.dataset.b);
    zeichne();
  });
  el.querySelector('.sl-kopieren').addEventListener('click', async (ev) => {
    const b = ev.target.closest('[data-kopiere]');
    if (!b) return;
    const pre = el.querySelector(`[data-teil="${b.dataset.kopiere}"]`);
    const meldung = el.querySelector('.sl-meldung');
    if (await kopiere(pre.textContent, navigator.clipboard) === 'kopiert') meldung.textContent = 'Kopiert.';
    else {
      const bereich = document.createRange();
      bereich.selectNodeContents(pre);
      getSelection().removeAllRanges();
      getSelection().addRange(bereich);
      meldung.textContent = 'Markiert, jetzt kopieren.';
    }
  });
  zeichne();
}
