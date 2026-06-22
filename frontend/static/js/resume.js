/**
 * resume.js — Resume builder page logic.
 * Handles tab switching, form data collection, API calls, preview rendering.
 */

// ── State ─────────────────────────────────────────────────────────────────────
let currentDocId  = null;
let activeTab     = 'quick';
let expCount      = 1;

// ── DOM refs ──────────────────────────────────────────────────────────────────
const generateBtn        = document.getElementById('generateBtn');
const downloadBtn        = document.getElementById('downloadBtn');
const statusBox          = document.getElementById('statusBox');
const statusText         = document.getElementById('statusText');
const previewPlaceholder = document.getElementById('previewPlaceholder');
const resumePreview      = document.getElementById('resumePreview');

// ── Tab switching ─────────────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('tab--active'));
    tab.classList.add('tab--active');
    activeTab = tab.dataset.tab;
    document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
    document.getElementById(`tab-${activeTab}`).classList.remove('hidden');
  });
});

// ── Add experience entry ──────────────────────────────────────────────────────
document.getElementById('addExp')?.addEventListener('click', () => {
  const list = document.getElementById('experienceList');
  const entry = document.createElement('div');
  entry.className = 'exp-entry form-group';
  entry.innerHTML = `
    <input class="form-input" placeholder="Role @ Company" data-field="role" />
    <input class="form-input" placeholder="Duration" data-field="duration" />
    <textarea class="form-textarea" rows="3" placeholder="Key achievements" data-field="bullets"></textarea>
    <button class="btn-add" style="color:#ef4444;align-self:flex-end" onclick="this.closest('.exp-entry').remove()">✕ Remove</button>
  `;
  list.appendChild(entry);
  expCount++;
});

// ── Collect form data ─────────────────────────────────────────────────────────
function collectFormData() {
  const userId = getUserId();

  if (activeTab === 'quick') {
    return {
      user_id:   userId,
      raw_input: document.getElementById('rawInput').value.trim(),
      name:      document.getElementById('name').value.trim(),
      title:     document.getElementById('title').value.trim(),
      email:     document.getElementById('email').value.trim(),
      phone:     document.getElementById('phone').value.trim(),
    };
  }

  // Detailed mode
  const expEntries = [...document.querySelectorAll('.exp-entry')].map(entry => ({
    role:     entry.querySelector('[data-field="role"]')?.value || '',
    duration: entry.querySelector('[data-field="duration"]')?.value || '',
    bullets:  (entry.querySelector('[data-field="bullets"]')?.value || '').split('\n').filter(Boolean),
  }));

  const educationEntries = [...document.querySelectorAll('.edu-entry')].map(entry => ({
    degree: entry.querySelector('[data-field="degree"]')?.value || '',
    institution: entry.querySelector('[data-field="institution"]')?.value || '',
    duration: entry.querySelector('[data-field="duration"]')?.value || '',
    gpa: entry.querySelector('[data-field="gpa"]')?.value || '',
  }));

  const projectEntries = [...document.querySelectorAll('.project-entry')].map(entry => ({
    name: entry.querySelector('[data-field="name"]')?.value || '',
    description: entry.querySelector('[data-field="description"]')?.value || '',
    tech: (entry.querySelector('[data-field="tech"]')?.value || '')
            .split(',')
            .map(t => t.trim())
            .filter(Boolean),
  }));

  const certEntries = [...document.querySelectorAll('.cert-entry')].map(entry => ({
    name: entry.querySelector('[data-field="name"]')?.value || '',
  }));

  return {
    user_id:    userId,
    raw_input:  `Summary: ${document.getElementById('summary')?.value || ''}. Skills: ${document.getElementById('skills')?.value || ''}`,
    summary:    document.getElementById('summary')?.value || '',
    skills:     document.getElementById('skills')?.value || '',
    experience: expEntries,
    education:  educationEntries,
    projects:   projectEntries,
    certifications: certEntries,
  };
}

// ── Generate ──────────────────────────────────────────────────────────────────
generateBtn.addEventListener('click', async () => {
  const data = collectFormData();

  if (!data.raw_input && activeTab === 'quick') {
    return showError('Please describe your experience before generating.');
  }

  setLoading(true, 'Generating your resume with AI…');

  try {
    const res  = await fetch('/api/resume/generate', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(data),
    });
    const json = await res.json();

    if (json.status !== 'success') throw new Error(json.message);

    currentDocId = json.doc_id;
    renderResumePreview(json.resume_data);
    downloadBtn.classList.remove('hidden');
  } catch (err) {
    showError('Generation failed: ' + err.message);
  } finally {
    setLoading(false);
  }
});

// ── Download ──────────────────────────────────────────────────────────────────
downloadBtn.addEventListener('click', () => {
  if (!currentDocId) return;
  window.location.href = `/api/resume/download/${currentDocId}`;
});

// ── Preview renderer ──────────────────────────────────────────────────────────
function renderResumePreview(r) {
  const skills = formatSkills(r.skills);
  const exp    = (r.experience || []).map(e => `
    <div class="rp-section">
      <div class="rp-job-title">${e.role || ''} — ${e.company || ''}</div>
      <div class="rp-job-meta">${e.duration || ''} · ${e.location || ''}</div>
      <ul>${(e.bullets || []).map(b => `<li>${b}</li>`).join('')}</ul>
    </div>`).join('');

  const edu = (r.education || []).map(e => {
    const gpa = e.gpa ? e.gpa.replace(/^CGPA:\s*/i, '').trim() : '';
    const meta = [e.duration, gpa ? 'CGPA: ' + gpa : ''].filter(Boolean).join(' · ');
    return `
    <div class="rp-section">
      <div class="rp-job-title">${e.degree || ''} — ${e.institution || ''}</div>
      <div class="rp-job-meta">${meta}</div>
    </div>`;
  }).join('');

  const projects = (r.projects || []).map(p => `
    <div class="rp-section">
      <div class="rp-job-title">${p.name || ''}</div>
      <div>${p.description || ''}</div>
      ${p.tech?.length ? `<div class="rp-job-meta">Tech: ${p.tech.join(', ')}</div>` : ''}
    </div>`).join('');

  resumePreview.innerHTML = `
    <h1>${r.name || ''}</h1>
    ${r.title   ? `<div class="rp-title">${r.title}</div>` : ''}
    <div class="rp-contact">${[r.email, r.phone, r.location, r.linkedin, r.github].filter(Boolean).join(' · ')}</div>
    <hr />
    ${r.summary ? `<h2>Summary</h2><p>${r.summary}</p><hr />` : ''}
    ${exp       ? `<h2>Experience</h2>${exp}<hr />` : ''}
    ${edu       ? `<h2>Education</h2>${edu}<hr />` : ''}
    ${skills    ? `<h2>Skills</h2>${skills}<hr />` : ''}
    ${projects  ? `<h2>Projects</h2>${projects}` : ''}
  `;

  previewPlaceholder.classList.add('hidden');
  resumePreview.classList.remove('hidden');
}

function formatSkills(skills) {
  if (!skills) return '';
  if (Array.isArray(skills)) {
    return `<div class="rp-skill-group">${skills.join(', ')}</div>`;
  }
  if (typeof skills === 'object') {
    return Object.entries(skills).map(([cat, list]) =>
      `<div class="rp-skill-group"><strong>${cat}:</strong> ${Array.isArray(list) ? list.join(', ') : list}</div>`
    ).join('');
  }
  return `<div class="rp-skill-group">${skills}</div>`;
}

// ── UI helpers ────────────────────────────────────────────────────────────────
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
