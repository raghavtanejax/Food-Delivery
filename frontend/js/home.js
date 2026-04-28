/**
 * home.js — Home page with notice board
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth()) return;
  renderNavbar();

  const noticeList = document.getElementById('notice-list');

  try {
    const notices = await apiRequest('/notices/');
    if (notices.length === 0) {
      noticeList.innerHTML = '<p style="color:var(--text-muted);font-size:0.9rem;">No announcements yet.</p>';
      return;
    }
    noticeList.innerHTML = notices.map(n => `
      <div class="notice-item">
        <h3>${escapeHtml(n.title)}</h3>
        <p>${escapeHtml(n.message)}</p>
        <div class="notice-time">${formatDate(n.created_at)}</div>
      </div>
    `).join('');
  } catch (err) {
    noticeList.innerHTML = '<p style="color:var(--danger);">Failed to load notices.</p>';
  }
});

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
