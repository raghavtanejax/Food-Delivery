/**
 * settings.js — Logic for Account Settings page
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth()) return;
  renderNavbar();

  // Tab switching logic
  const tabBtns = document.querySelectorAll('.tab-btn');
  const cards = document.querySelectorAll('.settings-card');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      cards.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-target');
      document.getElementById(targetId).classList.add('active');
    });
  });

  // Load Profile Data
  await loadProfileData();

  // Handle Profile Update
  const profileForm = document.getElementById('profile-form');
  profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btn-save-profile');
    
    const updates = {
      full_name: document.getElementById('prof-name').value,
      phone_number: document.getElementById('prof-phone').value,
      dob: document.getElementById('prof-dob').value
    };

    try {
      btn.disabled = true;
      btn.textContent = 'Saving...';
      const updatedUser = await apiRequest('/user/update', {
        method: 'PATCH',
        body: JSON.stringify(updates)
      });
      
      // Update local storage
      const currentUser = getUser();
      const newUser = { ...currentUser, ...updatedUser };
      localStorage.setItem('user', JSON.stringify(newUser));
      
      showToast('Profile updated successfully! ✅', 'success');
      renderNavbar(); // Refresh navbar name
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Save Changes';
    }
  });

  // Handle Password Change
  const passwordForm = document.getElementById('password-form');
  passwordForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const currentPassword = document.getElementById('pwd-current').value;
    const newPassword = document.getElementById('pwd-new').value;
    const confirmPassword = document.getElementById('pwd-confirm').value;
    const btn = document.getElementById('btn-change-pwd');

    if (newPassword !== confirmPassword) {
      showToast('New passwords do not match!', 'error');
      return;
    }

    try {
      btn.disabled = true;
      btn.textContent = 'Updating...';
      await apiRequest('/user/change-password', {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });
      showToast('Password changed successfully! 🔐', 'success');
      passwordForm.reset();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Update Password';
    }
  });

  // Payment Modal Logic
  const paymentModal = document.getElementById('payment-modal');
  const btnAddPayment = document.getElementById('btn-add-payment');
  const btnClosePayment = document.getElementById('btn-close-payment-modal');
  const paymentForm = document.getElementById('payment-form');

  btnAddPayment.addEventListener('click', () => {
    paymentModal.classList.add('open');
  });

  btnClosePayment.addEventListener('click', () => {
    paymentModal.classList.remove('open');
    paymentForm.reset();
  });

  paymentForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const cardNumber = document.getElementById('card-number').value;
    const last4 = cardNumber.slice(-4);
    const expiry = document.getElementById('card-expiry').value;

    const newPaymentHtml = `
      <div class="address-card">
        <h4>💳 Card ending in ${last4}</h4>
        <p>Expires ${expiry}</p>
      </div>
    `;
    
    document.getElementById('saved-payments').insertAdjacentHTML('beforeend', newPaymentHtml);
    paymentModal.classList.remove('open');
    paymentForm.reset();
    showToast('Payment method added successfully!', 'success');
  });
});

async function loadProfileData() {
  try {
    const user = await apiRequest('/user/me');
    document.getElementById('prof-name').value = user.name || '';
    document.getElementById('prof-email').value = user.email || '';
    document.getElementById('prof-phone').value = user.phone_number || '';
    document.getElementById('prof-dob').value = user.dob || '';
  } catch (err) {
    showToast('Failed to load profile data', 'error');
  }
}
