// Einstufung „Fahrkarte lösen“: drei Wissensfragen, je eine aus Linie E, A und B.
// Die erste Frage, die nicht richtig beantwortet ist, bestimmt den Einstieg.

const EINSTIEGE = [
  {linie: 'E', station: 'wie-ki-schreibt'},
  {linie: 'E', station: 'gut-fragen'},
  {linie: 'A', station: 'eigenes-material'},
];
const ALLES_RICHTIG = {linie: 'B', station: 'terminal'};

export function empfehlung(ergebnisse) {
  for (let i = 0; i < EINSTIEGE.length; i++) {
    if (ergebnisse[i] !== 'richtig') return {...EINSTIEGE[i]};
  }
  return {...ALLES_RICHTIG};
}
