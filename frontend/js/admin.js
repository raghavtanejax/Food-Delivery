/**
 * admin.js — Admin dashboard for menu management, orders, and notices
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAdmin()) return;
  renderNavbar();
  setupTabs();
  await loadAll();
});

/* --- Tab Navigation --- */
function setupTabs() {
  document.querySelectorAll('.admin-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(`section-${tab.dataset.tab}`).classList.add('active');
    });
  });
}

async function loadAll() {
  await Promise.all([loadStats(), loadMenuAdmin(), loadOrdersAdmin(), loadNoticesAdmin()]);
}

/* --- Stats --- */
async function loadStats() {
  try {
    const [menu, orders] = await Promise.all([
      apiRequest('/menu/'),
      apiRequest('/orders/all'),
    ]);

    document.getElementById('stat-items').textContent = menu.length;
    document.getElementById('stat-orders').textContent = orders.length;
    document.getElementById('stat-pending').textContent = orders.filter(o => o.status === 'pending').length;
    const revenue = orders.filter(o => o.status === 'delivered').reduce((s, o) => s + o.total, 0);
    document.getElementById('stat-revenue').textContent = formatPrice(revenue);
  } catch (err) {
    console.error('Stats error:', err);
  }
}

/* --- Menu Management --- */
let editingItemId = null;

async function loadMenuAdmin() {
  const tbody = document.getElementById('menu-table-body');
  try {
    const items = await apiRequest('/menu/');
    if (items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);">No menu items</td></tr>';
      return;
    }
    tbody.innerHTML = items.map(item => `
      <tr>
        <td><strong>${escapeHtml(item.name)}</strong></td>
        <td>${item.category}</td>
        <td>${formatPrice(item.price)}</td>
        <td>${item.available ? '✅' : '❌'}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="openEditItem('${item.id}', ${JSON.stringify(item).replace(/"/g, '&quot;')})">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteItem('${item.id}')">Delete</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="5" style="color:var(--danger);">Failed to load</td></tr>';
  }
}

function openAddItem() {
  editingItemId = null;
  document.getElementById('modal-title').textContent = 'Add Menu Item';
  document.getElementById('item-name').value = '';
  document.getElementById('item-desc').value = '';
  document.getElementById('item-price').value = '';
  document.getElementById('item-category').value = 'starters';
  document.getElementById('item-image').value = '';
  document.getElementById('item-available').checked = true;
  document.getElementById('item-modal').classList.add('open');
}

function openEditItem(id, item) {
  editingItemId = id;
  document.getElementById('modal-title').textContent = 'Edit Menu Item';
  document.getElementById('item-name').value = item.name;
  document.getElementById('item-desc').value = item.description;
  document.getElementById('item-price').value = item.price;
  document.getElementById('item-category').value = item.category;
  document.getElementById('item-image').value = item.image_url || '';
  document.getElementById('item-available').checked = item.available;
  document.getElementById('item-modal').classList.add('open');
}

function closeItemModal() {
  document.getElementById('item-modal').classList.remove('open');
}

async function saveItem() {
  const payload = {
    name: document.getElementById('item-name').value,
    description: document.getElementById('item-desc').value,
    price: parseFloat(document.getElementById('item-price').value),
    category: document.getElementById('item-category').value,
    image_url: document.getElementById('item-image').value,
    available: document.getElementById('item-available').checked,
  };

  try {
    if (editingItemId) {
      await apiRequest(`/menu/${editingItemId}`, { method: 'PUT', body: JSON.stringify(payload) });
      showToast('Item updated!', 'success');
    } else {
      await apiRequest('/menu/', { method: 'POST', body: JSON.stringify(payload) });
      showToast('Item added!', 'success');
    }
    closeItemModal();
    await loadMenuAdmin();
    await loadStats();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function deleteItem(id) {
  if (!confirm('Delete this menu item?')) return;
  try {
    await apiRequest(`/menu/${id}`, { method: 'DELETE' });
    showToast('Item deleted', 'success');
    await loadMenuAdmin();
    await loadStats();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/* --- Order Management --- */
async function loadOrdersAdmin() {
  const container = document.getElementById('admin-orders-list');
  try {
    const orders = await apiRequest('/orders/all');
    if (orders.length === 0) {
      container.innerHTML = '<div class="empty-state"><div class="emoji">📦</div><h3>No orders yet</h3></div>';
      return;
    }
    container.innerHTML = orders.map(order => `
      <div class="order-card" id="admin-order-${order.id}">
        <div class="order-header">
          <div>
            <span class="order-id">#${order.id.slice(-6).toUpperCase()}</span>
            <span style="color:var(--text-secondary);margin-left:0.5rem;">${escapeHtml(order.user_name)}</span>
          </div>
          <select class="status-select" onchange="updateStatus('${order.id}', this.value)">
            <option value="pending" ${order.status === 'pending' ? 'selected' : ''}>Pending</option>
            <option value="preparing" ${order.status === 'preparing' ? 'selected' : ''}>Preparing</option>
            <option value="out_for_delivery" ${order.status === 'out_for_delivery' ? 'selected' : ''}>Out for Delivery</option>
            <option value="delivered" ${order.status === 'delivered' ? 'selected' : ''}>Delivered</option>
          </select>
        </div>
        <ul class="order-items-list">
          ${order.items.map(i => `<li>• ${escapeHtml(i.name)} × ${i.quantity}</li>`).join('')}
        </ul>
        <div class="order-footer">
          <span style="color:var(--text-secondary)">${formatDate(order.created_at)}</span>
          <span class="price">${formatPrice(order.total)}</span>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div class="empty-state" style="color:var(--danger);">Failed to load orders</div>';
  }
}

async function updateStatus(orderId, newStatus) {
  try {
    await apiRequest(`/orders/${orderId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status: newStatus }),
    });
    showToast('Status updated!', 'success');
    await loadStats();
  } catch (err) {
    showToast(err.message, 'error');
    await loadOrdersAdmin();
  }
}

/* --- Notices Management --- */
async function loadNoticesAdmin() {
  const container = document.getElementById('admin-notices-list');
  try {
    const notices = await apiRequest('/notices/');
    if (notices.length === 0) {
      container.innerHTML = '<p style="color:var(--text-muted);">No notices posted yet.</p>';
      return;
    }
    container.innerHTML = notices.map(n => `
      <div class="notice-item" style="display:flex;justify-content:space-between;align-items:start;">
        <div>
          <h3>${escapeHtml(n.title)}</h3>
          <p>${escapeHtml(n.message)}</p>
          <div class="notice-time">${formatDate(n.created_at)}</div>
        </div>
        <button class="btn btn-danger btn-sm" onclick="deleteNotice('${n.id}')" style="flex-shrink:0;">Delete</button>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<p style="color:var(--danger);">Failed to load notices</p>';
  }
}

async function postNotice() {
  const title = document.getElementById('notice-title').value.trim();
  const message = document.getElementById('notice-message').value.trim();
  if (!title || !message) {
    showToast('Please fill in both fields', 'error');
    return;
  }
  try {
    await apiRequest('/notices/', { method: 'POST', body: JSON.stringify({ title, message }) });
    document.getElementById('notice-title').value = '';
    document.getElementById('notice-message').value = '';
    showToast('Notice posted! 📢', 'success');
    await loadNoticesAdmin();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function deleteNotice(id) {
  if (!confirm('Delete this notice?')) return;
  try {
    await apiRequest(`/notices/${id}`, { method: 'DELETE' });
    showToast('Notice deleted', 'success');
    await loadNoticesAdmin();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
