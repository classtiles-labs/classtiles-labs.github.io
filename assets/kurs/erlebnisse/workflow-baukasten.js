// Erlebnis „Workflows“: Schritte eines wiederkehrenden Auftrags ordnen, Regeln live prüfen und
// daraus eine fertige SKILL.md erzeugen, die Claude Code und Codex lesen.
import {kopiere} from '../ticket.js';

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function pruefe(reihe, regeln) {
  return regeln.map((r) => ({text: r.text, ok: reihe.indexOf(r.vor) < reihe.indexOf(r.nach)}));
}

export function verschiebe(reihe, index, richtung) {
  const ziel = index + richtung;
  if (ziel < 0 || ziel >= reihe.length) return [...reihe];
  const neu = [...reihe];
  [neu[index], neu[ziel]] = [neu[ziel], neu[index]];
  return neu;
}

export function alsSkill(kopf, reihe, schritte) {
  return [
    '---',
    `name: ${kopf.name}`,
    `description: ${kopf.beschreibung}`,
    '---',
    '',
    `# ${kopf.titel}`,
    '',
    ...reihe.map((id, i) => `${i + 1}. ${schritte[id]}`),
    '',
  ].join('\n');
}

export function mount(el, daten) {
  if (!daten?.start?.length) return;
  let reihe = [...daten.start];
  el.innerHTML = `
    <h2>Bau deinen ersten Workflow</h2>
    <p class="wf-anleitung">Jede Woche ein Arbeitsblatt mit Lösung. Bring die Schritte in eine sinnvolle Reihenfolge. Die Seite prüft dabei die Regeln, darunter entsteht die Datei für den Agenten.</p>
    <div class="wf-raster">
      <ol class="wf-reihe"></ol>
      <ul class="wf-regeln" aria-live="polite"></ul>
    </div>
    <p class="pb-label">SKILL.md</p>
    <pre class="pb-prompt wf-datei"></pre>
    <div class="wf-kopieren"><button type="button" class="btn b-line" data-kopieren></button> <span class="wf-meldung" role="status"></span></div>
    <ul class="wf-ablage">${daten.ablage.map((a) => `<li><b>${esc(a.app)}:</b> speichern als <code>${esc(a.pfad)}</code>, aufrufen mit <code>${esc(a.aufruf)}</code></li>`).join('')}</ul>
    <p class="ew-hinweis">${esc(daten.stand)}. Die Seite schreibt nur die Datei, sie startet keinen Agenten.</p>`;
  const liste = el.querySelector('.wf-reihe');
  const knopf = el.querySelector('[data-kopieren]');
  function zeichne(fokus) {
    liste.innerHTML = reihe.map((id, i) => `
      <li><span class="wf-text">${esc(daten.kurz[id])}</span>
        <span class="wf-pfeile">
          <button type="button" data-i="${i}" data-r="-1" aria-label="${esc(daten.kurz[id])} nach oben"${i === 0 ? ' disabled' : ''}>↑</button>
          <button type="button" data-i="${i}" data-r="1" aria-label="${esc(daten.kurz[id])} nach unten"${i === reihe.length - 1 ? ' disabled' : ''}>↓</button>
        </span></li>`).join('');
    const regeln = pruefe(reihe, daten.regeln);
    el.querySelector('.wf-regeln').innerHTML = regeln.map((r) => `<li class="${r.ok ? 'ok' : 'nein'}">${esc(r.text)}</li>`).join('');
    const fertig = regeln.every((r) => r.ok);
    el.querySelector('.wf-datei').textContent = alsSkill(daten.kopf, reihe, daten.schritte);
    knopf.disabled = !fertig;
    knopf.textContent = fertig ? 'SKILL.md kopieren' : 'Erst alle Regeln erfüllen';
    if (fokus) {
      const ziel = liste.querySelector(`[data-i="${fokus.i}"][data-r="${fokus.r}"]:not([disabled])`)
        ?? liste.querySelector(`[data-i="${fokus.i}"]:not([disabled])`);
      ziel?.focus();
    }
  }
  liste.addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-i]');
    if (!b || b.disabled) return;
    const i = Number(b.dataset.i);
    const r = Number(b.dataset.r);
    reihe = verschiebe(reihe, i, r);
    el.querySelector('.wf-meldung').textContent = '';
    zeichne({i: i + r, r});
  });
  knopf.addEventListener('click', async () => {
    const ergebnis = await kopiere(el.querySelector('.wf-datei').textContent, navigator.clipboard);
    const meldung = el.querySelector('.wf-meldung');
    if (ergebnis === 'kopiert') meldung.textContent = 'Kopiert.';
    else {
      const bereich = document.createRange();
      bereich.selectNodeContents(el.querySelector('.wf-datei'));
      getSelection().removeAllRanges();
      getSelection().addRange(bereich);
      meldung.textContent = 'Markiert, jetzt kopieren.';
    }
  });
  zeichne();
}
