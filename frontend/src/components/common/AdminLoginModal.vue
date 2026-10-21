<template>
  <div v-if="authStore.showLoginModal" class="modal-backdrop" @click.self="authStore.closeLoginModal">
    <div class="modal-card font-sans">
      <div class="modal-header">
        <div class="header-left">
          <div class="shield-box">
            <Icon name="shield" :size="16" />
          </div>
          <div>
            <h3 class="modal-title">Admin Authentication</h3>
            <p class="modal-subtitle">Sign in with an administrator account to access settings & controls.</p>
          </div>
        </div>
        <button class="modal-close-btn" @click="authStore.closeLoginModal">✕</button>
      </div>

      <div v-if="authStore.loginError" class="error-banner font-mono">
        <span>{{ authStore.loginError }}</span>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label class="form-label font-mono">Email Address</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="admin@subscriptiq.ai"
            class="form-input font-mono"
          />
        </div>

        <div class="form-group">
          <label class="form-label font-mono">Password</label>
          <input
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            class="form-input font-mono"
          />
        </div>

        <!-- Quick Fill Helper Buttons for instant demo testing -->
        <div class="quick-fill-section">
          <span class="quick-title font-mono">Demo Accounts:</span>
          <div class="quick-buttons">
            <button
              type="button"
              class="quick-fill-btn admin font-mono"
              @click="quickFill('admin@subscriptiq.ai', 'admin123')"
            >
              Fill Admin (admin123)
            </button>
            <button
              type="button"
              class="quick-fill-btn user font-mono"
              @click="quickFill('user@subscriptiq.ai', 'user123')"
            >
              Fill User (user123)
            </button>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel font-mono" @click="authStore.closeLoginModal">
            Cancel
          </button>
          <button type="submit" class="btn-submit font-mono" :disabled="isSubmitting">
            {{ isSubmitting ? 'Verifying...' : 'Sign In' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import Icon from '@/components/common/Icon.vue'

const authStore = useAuthStore()
const uiStore = useUIStore()

const email = ref('admin@subscriptiq.ai')
const password = ref('admin123')
const isSubmitting = ref(false)

function quickFill(userEmail, userPass) {
  email.value = userEmail
  password.value = userPass
}

async function handleLogin() {
  isSubmitting.value = true
  const success = await authStore.login(email.value, password.value)
  isSubmitting.value = false
  if (success && authStore.isAdmin && !uiStore.activeNav.startsWith('admin')) {
    uiStore.setActiveNav('admin-schema')
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-card {
  width: 100%;
  max-width: 440px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 20px;
  animation: fadeIn 0.15s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.97); }
  to { opacity: 1; transform: scale(1); }
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.shield-box {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background-color: var(--accent-light);
  border: 1px solid rgba(var(--accent-rgb), 0.3);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-title {
  font-size: var(--text-md);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0 0 2px 0;
}

.modal-subtitle {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin: 0;
}

.modal-close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 14px;
  cursor: pointer;
  padding: 4px;
}

.modal-close-btn:hover {
  color: var(--text-primary);
}

.error-banner {
  background-color: var(--danger-bg);
  border: 1px solid var(--danger);
  color: var(--danger);
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  margin-bottom: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.form-input {
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  padding: 8px 10px;
  font-size: 12px;
  outline: none;
  transition: border-color var(--transition-fast);
}

.form-input:focus {
  border-color: var(--accent);
}

.quick-fill-section {
  background-color: var(--bg-primary);
  border: 1px dashed var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 4px;
}

.quick-title {
  font-size: 10px;
  color: var(--text-muted);
}

.quick-buttons {
  display: flex;
  gap: 8px;
}

.quick-fill-btn {
  font-size: 10.5px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex: 1;
}

.quick-fill-btn.admin:hover {
  border-color: var(--accent);
  color: var(--accent);
  background-color: var(--bg-active);
}

.quick-fill-btn.user:hover {
  border-color: var(--text-muted);
  color: var(--text-primary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.btn-cancel {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  cursor: pointer;
}

.btn-submit {
  background: var(--btn-primary-gradient);
  border: 1px solid var(--btn-primary-border);
  color: #ffffff;
  padding: 6px 18px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
  transition: all var(--transition-fast);
}

.btn-submit:hover:not(:disabled) {
  background: var(--btn-primary-gradient-hover);
  border-color: rgba(56, 189, 248, 0.5);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
