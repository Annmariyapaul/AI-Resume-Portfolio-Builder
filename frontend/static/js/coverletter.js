/**
 * coverletter.js — Cover letter builder page logic.
 */

let currentDocId = null;

const generateBtn        = document.getElementById('generateBtn');
const downloadBtn        = document.getElementById('downloadBtn');
const statusBox          = document.getElementById('statusBox');
const statusText         = document.getElementById('statusText');
const previewPlaceholder = document.getElementById('previewPlaceholder');
const coverPreview       = document.getElementById('coverPreview');

generateBtn.addEventListener('click', async () => {
  const data = {
    user_id:        getUserId(),
    name:           document.getElementById('name').value.trim(),
    email:          document.getElementById('email').value.trim(),
    phone:          document.getElementById('phone').value.trim(),
    job_title:      document.getElementById('jobTitle').value.trim(),
    company:        document.getElementById('company').value.trim(),
    recipient_name: document.getElementById('recipientName').value.trim(),
    job_description:document.getElementById('jobDescription').value.trim(),
    resume_summary: document.getElementById('resumeSummary').value.trim(),
  };

  if (!data.job_title || !data.company) {
    return showError('Job title and company are required.');
  }

  setLoading(true, 'Writing your cover letter…');

  try {
    const res  = await fetch('/api/cover-letter/generate', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(data),
    });
    const json = await res.json();
    if (json.status !== 'success') throw new Error(json.message);

    currentDocId = json.doc_id;
    renderPreview(json.cover_data);
    downloadBtn.classList.remove('hidden');
  } catch (err) {
    showError('Error: ' + err.message);
  } finally {
    setLoading(false);
  }
});

downloadBtn.addEventListener('click', () => {
  if (currentDocId) window.location.href = `/api/cover-letter/download/${currentDocId}`;
});

function renderPreview(c) {
  const today = new Date().toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' });
  const paras = (c.body || '').split('\n\n').filter(Boolean).map(p => `<p>${p}</p>`).join('');

  coverPreview.innerHTML = `
    <div class="cl-sender">
      <strong>${c.name || ''}</strong><br/>
      ${[c.email, c.phone].filter(Boolean).join(' · ')}
    </div>
    <p>${today}</p>
    <p>
      ${c.recipient_name || 'Hiring Manager'}<br/>
      ${c.recipient_title ? c.recipient_title + '<br/>' : ''}
      ${c.company || ''}
    </p>
    <p>Dear ${c.recipient_name || 'Hiring Manager'},</p>
    ${paras}
    <p>${c.closing || 'Sincerely'},</p>
    <p style="margin-top:2rem"><strong>${c.name || ''}</strong></p>
  `;

  previewPlaceholder.classList.add('hidden');
  coverPreview.classList.remove('hidden');
}

function setLoading(on, msg = '') {
  statusBox.classList.toggle('hidden', !on);
  generateBtn.disabled = on;
  if (msg) statusText.textContent = msg;
}

function showError(msg) {
  statusText.textContent = '⚠ ' + msg;
  statusBox.classList.remove('hidden');
  setTimeout(() => statusBox.classList.add('hidden'), 5000);
}
