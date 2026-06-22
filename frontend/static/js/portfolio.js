/**
 * portfolio.js — Portfolio builder page logic.
 */

let currentDocId = null;

const generateBtn        = document.getElementById('generateBtn');
const copyLinkBtn        = document.getElementById('copyLinkBtn');
const statusBox          = document.getElementById('statusBox');
const statusText         = document.getElementById('statusText');
const previewPlaceholder = document.getElementById('previewPlaceholder');
const portfolioPreview   = document.getElementById('portfolioPreview');

// ── Add project entry ─────────────────────────────────────────────────────────
document.getElementById('addProject')?.addEventListener('click', () => {
  const list  = document.getElementById('projectsList');
  const entry = document.createElement('div');
  entry.className = 'project-entry';
  entry.innerHTML = `
    <input class="form-input" placeholder="Project name" data-field="name" />
    <input class="form-input" placeholder="Short description" data-field="description" />
    <input class="form-input" placeholder="GitHub / Live URL" data-field="link" />
    <input class="form-input" placeholder="Tech stack (comma-separated)" data-field="tech" />
    <button class="btn-add" style="color:#ef4444;align-self:flex-end" onclick="this.closest('.project-entry').remove()">✕ Remove</button>
  `;
  list.appendChild(entry);
});

// ── Collect form data ─────────────────────────────────────────────────────────
function collectData() {
  const projects = [...document.querySelectorAll('.project-entry')].map(e => ({
    name:        e.querySelector('[data-field="name"]')?.value || '',
    description: e.querySelector('[data-field="description"]')?.value || '',
    link:        e.querySelector('[data-field="link"]')?.value || '',
    tech:        (e.querySelector('[data-field="tech"]')?.value || '').split(',').map(s => s.trim()).filter(Boolean),
  })).filter(p => p.name);

  return {
    user_id:  getUserId(),
    name:     document.getElementById('name').value.trim(),
    title:    document.getElementById('title').value.trim(),
    bio:      document.getElementById('bio').value.trim(),
    skills:   document.getElementById('skills').value.split(',').map(s => s.trim()).filter(Boolean),
    projects,
    socials: {
      github:   document.getElementById('github').value.trim(),
      linkedin: document.getElementById('linkedin').value.trim(),
      email:    document.getElementById('email').value.trim(),
    },
  };
}

// ── Generate ──────────────────────────────────────────────────────────────────
generateBtn.addEventListener('click', async () => {
  const data = collectData();
  if (!data.name) return showError('Your name is required.');

  setLoading(true, 'Building your portfolio…');

  try {
    const res  = await fetch('/api/portfolio/generate', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(data),
    });
    const json = await res.json();
    if (json.status !== 'success') throw new Error(json.message);

    currentDocId = json.doc_id;
    renderPreview(json.portfolio_data);
    copyLinkBtn.classList.remove('hidden');
  } catch (err) {
    showError('Error: ' + err.message);
  } finally {
    setLoading(false);
  }
});

copyLinkBtn.addEventListener('click', () => {
  const link = `${window.location.origin}/portfolio/${currentDocId}`;
  navigator.clipboard.writeText(link).then(() => {
    copyLinkBtn.textContent = '✓ Link copied!';
    setTimeout(() => { copyLinkBtn.textContent = '🔗 Copy Share Link'; }, 2000);
  });
});

// ── Preview renderer ──────────────────────────────────────────────────────────
function renderPreview(p) {
  const skills   = (p.skills || []).map(s => `<span class="pp-skill">${s}</span>`).join('');
  const projects = (p.projects || []).map(pr => `
    <div class="pp-project-card">
      <h4>${pr.name || ''}</h4>
      <p>${pr.description || ''}</p>
      ${pr.tech?.length ? `<p style="font-size:.78rem;color:var(--accent);margin-top:.5rem">${pr.tech.join(' · ')}</p>` : ''}
      ${pr.link ? `<a href="${pr.link}" target="_blank" style="font-size:.82rem;color:var(--accent)">View →</a>` : ''}
    </div>`).join('');

  const socials = p.socials || {};
  const socialLinks = [
    socials.github   ? `<a href="${socials.github}"   target="_blank">GitHub</a>` : '',
    socials.linkedin ? `<a href="${socials.linkedin}" target="_blank">LinkedIn</a>` : '',
    socials.email    ? `<a href="mailto:${socials.email}">Email</a>` : '',
  ].filter(Boolean).join(' · ');

  portfolioPreview.innerHTML = `
    <div class="pp-header">
      <h1>${p.name || ''}</h1>
      <p style="color:var(--accent);font-weight:600;margin:.3rem 0">${p.title || ''}</p>
      <p style="font-size:.88rem;color:var(--grey)">${socialLinks}</p>
    </div>
    ${p.enhanced_bio ? `<div class="pp-bio">${p.enhanced_bio}</div>` : ''}
    ${skills ? `<div class="pp-section-title">Skills</div><div class="pp-skills">${skills}</div>` : ''}
    ${projects ? `<div class="pp-section-title">Projects</div><div class="pp-projects">${projects}</div>` : ''}
  `;

  previewPlaceholder.classList.add('hidden');
  portfolioPreview.classList.remove('hidden');
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
