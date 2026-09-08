(() => {
  const key = 'mathintegrity-planner-welcome-v2';
  const popup = document.getElementById('planner-welcome');
  if (!popup) return;
  try { if (localStorage.getItem(key)) return; } catch { /* Storage is optional. */ }
  const dismiss = () => {
    popup.hidden = true;
    try { localStorage.setItem(key, 'seen'); } catch {}
    document.removeEventListener('pointerdown', outside);
    document.removeEventListener('keydown', escape);
  };
  const outside = event => { if (!popup.parentElement.contains(event.target)) dismiss(); };
  const escape = event => { if (event.key === 'Escape') dismiss(); };
  document.getElementById('planner-welcome-dismiss').addEventListener('click', () => {
    dismiss(); popup.parentElement.querySelector('.planner-launch-button').focus({ preventScroll: true });
  });
  document.getElementById('planner-welcome-open').addEventListener('click', dismiss);
  document.addEventListener('pointerdown', outside);
  document.addEventListener('keydown', escape);
  popup.hidden = false;
  try { localStorage.setItem(key, 'seen'); } catch {}
})();
