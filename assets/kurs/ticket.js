// Ticket kopieren: Zwischenablage, wenn der Browser sie hergibt; sonst sagt die Seite
// „markieren“ und markiert den Text, damit man ihn selbst kopieren kann.

export async function kopiere(text, zwischenablage) {
  if (!zwischenablage || typeof zwischenablage.writeText !== 'function') return 'markieren';
  try {
    await zwischenablage.writeText(text);
    return 'kopiert';
  } catch {
    return 'markieren';
  }
}
