/**
 * auth.js — Login and Signup logic for index.html
 */

document.addEventListener('DOMContentLoaded', () => {
  // If already logged in, redirect to home
  if (isAuthenticated()) {
    navigateTo('/home');
    return;
  }

  const loginForm = document.getElementById('login-form');
  const signupForm = document.getElementById('signup-form');
  const showSignup = document.getElementById('show-signup');
  const showLogin = document.getElementById('show-login');
  const loginSection = document.getElementById('login-section');
  const signupSection = document.getElementById('signup-section');

  // Toggle between login and signup
  showSignup.addEventListener('click', (e) => {
    e.preventDefault();
    loginSection.style.display = 'none';
    signupSection.style.display = 'block';
  });

  showLogin.addEventListener('click', (e) => {
    e.preventDefault();
    signupSection.style.display = 'none';
    loginSection.style.display = 'block';
  });

  // Role is always customer for new signups
  const selectedRole = 'customer';


  // Login handler
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const btn = loginForm.querySelector('button[type="submit"]');

    try {
      btn.disabled = true;
      btn.textContent = 'Signing in...';
      const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      saveAuth(data);
      showToast('Welcome back! 👋', 'success');
      setTimeout(() => navigateTo('/home'), 500);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Sign In';
    }
  });

  // Signup handler
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const btn = signupForm.querySelector('button[type="submit"]');

    try {
      btn.disabled = true;
      btn.textContent = 'Creating account...';
      const data = await apiRequest('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ name, email, password, role: selectedRole }),
      });
      saveAuth(data);
      showToast('Account created successfully! 🎉', 'success');
      setTimeout(() => navigateTo('/home'), 500);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Create Account';
    }
  });
});
