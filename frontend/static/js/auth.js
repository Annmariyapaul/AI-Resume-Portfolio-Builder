/**
 * auth.js — Firebase Authentication (Google Sign-in).
 * Replace firebaseConfig with your actual project credentials.
 */

// ── Config (replace with your Firebase project values) ──────────────────────
const firebaseConfig = {
  apiKey:            "AIzaSyBy0SazbcXi4VusJ0PTH4TAsM5YM5aNeaE",
  authDomain:        "careerai-686ef.firebaseapp.com",
  projectId:         "careerai-686ef",
  storageBucket:     "careerai-686ef.firebasestorage.app",
  messagingSenderId: "692512817732",
  appId:             "1:692512817732:web:72d317ae6dabe61786f211",
};

// ── Init (guarded — Firebase script must load before this) ───────────────────
let auth = null;

function initFirebase() {
  if (typeof firebase === 'undefined') return;
  if (!firebase.apps.length) firebase.initializeApp(firebaseConfig);
  auth = firebase.auth();

  // Persist user state in localStorage for cross-page access
  auth.onAuthStateChanged(user => {
    if (user) {
      localStorage.setItem('careerai_user', JSON.stringify({
        uid:         user.uid,
        displayName: user.displayName,
        email:       user.email,
        photoURL:    user.photoURL,
      }));
      updateNavForUser(user);
    } else {
      localStorage.removeItem('careerai_user');
      updateNavForGuest();
    }
  });
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function getCurrentUser() {
  const raw = localStorage.getItem('careerai_user');
  return raw ? JSON.parse(raw) : null;
}

function getUserId() {
  const u = getCurrentUser();
  // Fall back to a session-scoped guest ID so the app still works without auth
  if (!u) {
    if (!sessionStorage.getItem('guest_id')) {
      sessionStorage.setItem('guest_id', 'guest_' + Math.random().toString(36).slice(2));
    }
    return sessionStorage.getItem('guest_id');
  }
  return u.uid;
}

function signInWithGoogle() {
  if (!auth) return alert('Firebase not initialised.');
  const provider = new firebase.auth.GoogleAuthProvider();
  auth.signInWithPopup(provider).catch(console.error);
}

function signOut() {
  if (!auth) return;
  auth.signOut();
}

function updateNavForUser(user) {
  const btn = document.getElementById('loginBtn');
  if (!btn) return;
  btn.textContent = user.displayName?.split(' ')[0] || 'Account';
  btn.onclick = () => signOut();
}

function updateNavForGuest() {
  const btn = document.getElementById('loginBtn');
  if (!btn) return;
  btn.textContent = 'Sign In';
  btn.onclick = () => openAuthModal();
}

function openAuthModal() {
  const modal = document.getElementById('authModal');
  if (modal) modal.classList.add('is-open');
}

// ── Modal wiring ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initFirebase();

  const closeBtn = document.getElementById('closeModal');
  if (closeBtn) closeBtn.addEventListener('click', () => {
    document.getElementById('authModal').classList.remove('is-open');
  });

  const loginBtn = document.getElementById('loginBtn');
  if (loginBtn) loginBtn.addEventListener('click', () => openAuthModal());

  // Google sign-in button inside modal (if present)
  const googleBtn = document.getElementById('googleSignInBtn');
  if (googleBtn) googleBtn.addEventListener('click', signInWithGoogle);
});
