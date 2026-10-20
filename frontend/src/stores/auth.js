import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // Current user state with role ('admin' or 'user')
  const user = ref({
    name: 'Alex Rivera',
    email: 'alex.rivera@subscriptiq.ai',
    role: 'admin', // default to admin so user can see admin section, and toggle anytime
    avatar: 'AR',
  })

  const isAdmin = computed(() => user.value.role === 'admin')

  function toggleRole() {
    user.value.role = user.value.role === 'admin' ? 'user' : 'admin'
  }

  function setRole(newRole) {
    user.value.role = newRole
  }

  return {
    user,
    isAdmin,
    toggleRole,
    setRole,
  }
})
