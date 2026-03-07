/* Report Integrity Concern — form submission */

// ── Replace this with your deployed Google Apps Script web app URL ──
const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbzvj1tVhYBlV2ycx-VJIxa4rJ5bUzKYnlqv8_Hy1-Bh2b-zZ_3-_I7AWvqqza8eFloR/exec';

const form = document.getElementById('report-form');
const submitBtn = document.getElementById('report-submit');
const statusEl = document.getElementById('report-status');

// ── Fetch client IP for logging ───────────────────────────────────
async function getClientIP() {
  try {
    const resp = await fetch('https://api.ipify.org?format=json');
    const json = await resp.json();
    return json.ip;
  } catch {
    return 'unknown';
  }
}

// ── Submit report ──────────────────────────────────────────────────
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  if (document.getElementById('website').value) return;

  const data = {
    name: document.getElementById('reported-name').value.trim(),
    state: document.getElementById('reported-state').value,
    contest: document.getElementById('reported-contest').value.trim(),
    description: document.getElementById('reported-description').value.trim(),
  };

  if (!data.name || !data.state || !data.contest || !data.description) {
    showStatus('Please fill in the required fields.', 'error');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Submitting…';
  showStatus('', '');

  try {
    data.ip = await getClientIP();
    const resp = await fetch(APPS_SCRIPT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: JSON.stringify(data),
    });
    const result = await resp.json();
    if (result.error) {
      showStatus(result.error, 'error');
    } else {
      showStatus('Report submitted. Thank you.', 'success');
      form.reset();
    }
  } catch (err) {
    showStatus('Failed to submit. Please try again later.', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Report';
  }
});

function showStatus(msg, type) {
  statusEl.textContent = msg;
  statusEl.className = 'report-status' + (type ? ' report-status--' + type : '');
}
