(() => {
  const key = 'mathintegrity-planner-welcome-v1';
  const dialog = document.getElementById('planner-welcome');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  try { if (localStorage.getItem(key)) return; } catch { /* Browsing still works without storage. */ }
  const remember = () => { try { localStorage.setItem(key, 'seen'); } catch {} };
  document.getElementById('planner-welcome-dismiss').addEventListener('click', () => dialog.close());
  document.getElementById('planner-welcome-open').addEventListener('click', remember);
  dialog.addEventListener('close', remember);
  dialog.addEventListener('cancel', remember);
  dialog.showModal();
  remember();
})();
