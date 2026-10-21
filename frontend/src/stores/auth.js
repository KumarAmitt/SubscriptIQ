import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const useAuthStore = defineStore('auth', () => {
  const savedToken = localStorage.getItem('subscriptiq_token') || ''
  const savedUser = localStorage.getItem('subscriptiq_user')

  const token = ref(savedToken)
  const user = ref(
    savedUser
      ? JSON.parse(savedUser)
      : {
          name: 'Sarah Chen',
          email: 'user@subscriptiq.ai',
          role: 'user', // Default is standard user (non-admin)
          avatar: 'SC',
        }
  )

  const showLoginModal = ref(false)
  const loginError = ref('')

  const isAdmin = computed(() => user.value && user.value.role === 'admin')

  function getAuthHeaders() {
    const headers = { 'Content-Type': 'application/json' }
    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`
    }
    return headers
  }

  async function login(email, password) {
    loginError.value = ''
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password: password.trim() }),
      })

      const data = await res.json()
      if (!res.ok) {
        loginError.value = data.detail || 'Authentication failed'
        return false
      }

      token.value = data.access_token
      user.value = {
        id: data.user.id,
        name: data.user.name,
        email: data.user.email,
        role: data.user.role,
        avatar: data.user.name
          .split(' ')
          .map((n) => n[0])
          .join('')
          .toUpperCase(),
      }

      localStorage.setItem('subscriptiq_token', token.value)
      localStorage.setItem('subscriptiq_user', JSON.stringify(user.value))
      showLoginModal.value = false
      return true
    } catch (err) {
      loginError.value = 'Could not connect to authentication server: ' + err.message
      return false
    }
  }

  function logout() {
    token.value = ''
    user.value = {
      name: 'Sarah Chen',
      email: 'user@subscriptiq.ai',
      role: 'user',
      avatar: 'SC',
    }
    localStorage.removeItem('subscriptiq_token')
    localStorage.removeItem('subscriptiq_user')
  }

  function openLoginModal() {
    loginError.value = ''
    showLoginModal.value = true
  }

  function closeLoginModal() {
    showLoginModal.value = false
  }

  return {
    token,
    user,
    isAdmin,
    showLoginModal,
    loginError,
    getAuthHeaders,
    login,
    logout,
    openLoginModal,
    closeLoginModal,
  }
})
