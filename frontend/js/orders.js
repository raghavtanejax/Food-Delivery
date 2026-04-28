/**
 * orders.js — Order history page for customers
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth()) return;
  renderNavbar();
  await loadOrders();
});

async function loadOrders() {
  const container = document.getElementById('orders-list');
  container.innerHTML = '<div class="spinner"></div>';

  try {
    const orders = await apiRequest('/orders/my');

    if (orders.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="emoji">📦</div>
          <h3>No orders yet</h3>
          <p>Place your first order from our delicious menu!</p>
          <br>
          <a href="/menu" class="btn btn-primary">Browse Menu</a>
        </div>
      `;
      return;
    }

    container.innerHTML = orders.map(order => `
      <div class="order-card" id="order-${order.id}">
        <div class="order-header">
          <span class="order-id">#${order.id.slice(-6).toUpperCase()}</span>
          <span class="status-badge status-${order.status}">${formatStatus(order.status)}</span>
        </div>
        <ul class="order-items-list">
          ${order.items.map(i => `<li>• ${escapeHtml(i.name)} × ${i.quantity} — ${formatPrice(i.price * i.quantity)}</li>`).join('')}
        </ul>
        <div class="order-footer">
          <span style="color:var(--text-secondary)">${formatDate(order.created_at)}</span>
          <span class="price">${formatPrice(order.total)}</span>
        </div>
        <div class="order-footer" style="padding-top: 0.5rem; border-top: none; font-size: 0.85rem; color: var(--text-muted);">
          <span>💳 Paid via ${order.payment_method}</span>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div class="empty-state"><div class="emoji">😞</div><h3>Failed to load orders</h3></div>';
  }
}

function formatStatus(status) {
  const map = {
    pending: 'Pending',
    preparing: 'Preparing',
    out_for_delivery: 'Out for Delivery',
    delivered: 'Delivered',
  };
  return map[status] || status;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
