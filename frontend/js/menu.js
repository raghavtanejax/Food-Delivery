/**
 * menu.js — Menu display with category filtering and cart functionality
 */

let menuItems = [];
let cart = JSON.parse(localStorage.getItem('cart') || '[]');
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth()) return;
  renderNavbar();
  await loadMenu();
  setupFilters();
  updateCartUI();
});

async function loadMenu() {
  const grid = document.getElementById('menu-grid');
  grid.innerHTML = '<div class="spinner"></div>';

  try {
    menuItems = await apiRequest('/menu/');
    renderMenu();
  } catch (err) {
    grid.innerHTML = '<div class="empty-state"><div class="emoji">😞</div><h3>Failed to load menu</h3></div>';
  }
}

function renderMenu() {
  const grid = document.getElementById('menu-grid');
  const filtered = currentFilter === 'all' ? menuItems : menuItems.filter(i => i.category === currentFilter);

  if (filtered.length === 0) {
    grid.innerHTML = '<div class="empty-state"><div class="emoji">🍽️</div><h3>No items in this category</h3></div>';
    return;
  }

  grid.innerHTML = filtered.map(item => {
    const inCart = cart.find(c => c.item_id === item.id);
    const qty = inCart ? inCart.quantity : 0;

    return `
      <div class="menu-card" id="menu-item-${item.id}">
        <img class="menu-card-img" src="${item.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400'}" 
             alt="${escapeHtml(item.name)}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400'" />
        <div class="menu-card-body">
          <h3>${escapeHtml(item.name)}</h3>
          <p class="description">${escapeHtml(item.description)}</p>
          <div class="menu-card-footer">
            <span class="price">${formatPrice(item.price)}</span>
            ${item.available === false
              ? `<span class="badge" style="color:var(--danger); background:var(--danger-bg); padding:0.4rem 0.8rem; border-radius: var(--radius-sm); font-size:0.8rem; font-weight:600;">Out of Stock</span>`
              : qty === 0 
                ? `<button class="btn btn-primary btn-sm" onclick="addToCart('${item.id}')">+ Add</button>`
                : `<div class="qty-control">
                     <button class="qty-btn" onclick="updateQty('${item.id}', -1)">−</button>
                     <span class="qty-display">${qty}</span>
                     <button class="qty-btn" onclick="updateQty('${item.id}', 1)">+</button>
                   </div>`
            }
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function setupFilters() {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.category;
      renderMenu();
    });
  });
}

function addToCart(itemId) {
  const item = menuItems.find(i => i.id === itemId);
  if (!item) return;

  if (item.available === false) {
    showToast('Item is currently out of stock', 'error');
    return;
  }

  const existing = cart.find(c => c.item_id === itemId);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ item_id: item.id, name: item.name, price: item.price, quantity: 1 });
  }

  saveCart();
  renderMenu();
  updateCartUI();
  showToast(`${item.name} added to cart`, 'success');
}

function updateQty(itemId, delta) {
  const existing = cart.find(c => c.item_id === itemId);
  if (!existing) return;

  existing.quantity += delta;
  if (existing.quantity <= 0) {
    cart = cart.filter(c => c.item_id !== itemId);
  }

  saveCart();
  renderMenu();
  updateCartUI();
}

function saveCart() {
  localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartUI() {
  const badge = document.getElementById('cart-count');
  const totalItems = cart.reduce((sum, c) => sum + c.quantity, 0);
  badge.textContent = totalItems;
  badge.style.display = totalItems > 0 ? 'flex' : 'none';

  renderCartSidebar();
}

function renderCartSidebar() {
  const container = document.getElementById('cart-items');
  const totalEl = document.getElementById('cart-total-price');
  const checkoutBtn = document.getElementById('btn-checkout');

  if (cart.length === 0) {
    container.innerHTML = '<div class="cart-empty">🛒 Your cart is empty</div>';
    totalEl.textContent = '₹0';
    checkoutBtn.disabled = true;
    return;
  }

  checkoutBtn.disabled = false;
  const total = cart.reduce((sum, c) => sum + c.price * c.quantity, 0);
  totalEl.textContent = formatPrice(total);

  container.innerHTML = cart.map(c => `
    <div class="cart-item">
      <div class="cart-item-info">
        <h4>${escapeHtml(c.name)}</h4>
        <p>${c.quantity} × ${formatPrice(c.price)} = ${formatPrice(c.price * c.quantity)}</p>
      </div>
      <button class="cart-item-remove" onclick="removeFromCart('${c.item_id}')">✕</button>
    </div>
  `).join('');
}

function removeFromCart(itemId) {
  cart = cart.filter(c => c.item_id !== itemId);
  saveCart();
  renderMenu();
  updateCartUI();
}

function toggleCart() {
  document.getElementById('cart-sidebar').classList.toggle('open');
  document.getElementById('cart-overlay').classList.toggle('open');
}

async function checkout() {
  const address = document.getElementById('checkout-address').value.trim();
  const paymentMethod = document.getElementById('checkout-payment').value;
  if (!address) {
    showToast('Please enter a delivery address', 'error');
    return;
  }
  if (cart.length === 0) {
    showToast('Cart is empty', 'error');
    return;
  }

  const btn = document.getElementById('btn-checkout');
  try {
    btn.disabled = true;
    btn.textContent = 'Placing order...';

    await apiRequest('/orders/', {
      method: 'POST',
      body: JSON.stringify({ items: cart, address, payment_method: paymentMethod }),
    });

    cart = [];
    saveCart();
    updateCartUI();
    toggleCart();
    showToast('Order placed successfully! 🎉', 'success');
    setTimeout(() => navigateTo('/orders'), 1000);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Place Order';
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
