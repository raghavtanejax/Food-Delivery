/**
 * api.js — Centralized API helper with JWT token management.
 */

const API_BASE = '/api';

/** Get the stored JWT token. */
function getToken() {
  return localStorage.getItem('token');
}

/** Get the stored user object. */
function getUser() {
  const u = localStorage.getItem('user');
  return u ? JSON.parse(u) : null;
}

/** Save auth data after login/signup. */
function saveAuth(data) {
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
}

/** Clear auth data on logout. */
function clearAuth() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

/** Check if user is authenticated. */
function isAuthenticated() {
  return !!getToken();
}

/** Check if current user is admin. */
function isAdmin() {
  const user = getUser();
  return user && user.role === 'admin';
}

/**
 * Make an API request with optional JWT auth.
 * @param {string} endpoint - API path (e.g., '/auth/login')
 * @param {object} options - fetch options
 * @returns {Promise<any>}
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, { ...options, headers });

  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const msg = data?.detail || `Request failed (${response.status})`;
    throw new Error(msg);
  }

  return data;
}

/** Show a toast notification. */
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => toast.remove(), 3000);
}

/** Redirect helper. */
function navigateTo(path) {
  window.location.href = path;
}

/** Require authentication — redirect to login if not authenticated. */
function requireAuth() {
  if (!isAuthenticated()) {
    navigateTo('/');
    return false;
  }
  return true;
}

/** Require admin role — redirect if not admin. */
function requireAdmin() {
  if (!requireAuth()) return false;
  if (!isAdmin()) {
    showToast('Admin access required', 'error');
    navigateTo('/home');
    return false;
  }
  return true;
}

/** Format price in INR. */
function formatPrice(amount) {
  return `₹${parseFloat(amount).toFixed(0)}`;
}

/** Format datetime string for display. */
function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

/** Render the navbar based on auth state and role. */
function renderNavbar() {
  const user = getUser();
  const nav = document.getElementById('navbar-links');
  if (!nav) return;

  let links = '';
  if (user) {
    links += `<a href="/home" class="nav-link" id="nav-home">🏠 Home</a>`;
    links += `<a href="/menu" class="nav-link" id="nav-menu">🍽️ Menu</a>`;
    links += `<a href="/orders" class="nav-link" id="nav-orders">📦 Orders</a>`;
    links += `<a href="/settings" class="nav-link" id="nav-settings">⚙️ Settings</a>`;
    if (user.role === 'admin') {
      links += `<a href="/admin" class="nav-link" id="nav-admin">📊 Dashboard</a>`;
    }
    links += `<span class="nav-link" style="color:var(--text-muted);">Hi, ${user.name}</span>`;
    links += `<button class="nav-link btn-logout" id="btn-logout" onclick="handleLogout()">Logout</button>`;
  }
  nav.innerHTML = links;
}

/** Handle logout. */
function handleLogout() {
  clearAuth();
  navigateTo('/');
}
