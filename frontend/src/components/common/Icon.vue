<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="svg-icon"
  >
    <!-- Dashboard / Grid -->
    <path
      v-if="name === 'dashboard'"
      d="M3 3h7v7H3V3zm11 0h7v4h-7V3zm0 8h7v10h-7V11zm-11 3h7v7H3v-7z"
    />

    <!-- Admin / Shield -->
    <path
      v-else-if="name === 'admin' || name === 'shield'"
      d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z M12 8v4 M12 16h.01"
    />

    <!-- Sparkles / AI Copilot -->
    <path
      v-else-if="name === 'sparkles' || name === 'ai'"
      d="m12 3 1.9 4.6L18.5 9.5l-4.6 1.9L12 16l-1.9-4.6-4.6-1.9 4.6-1.9L12 3zm7 13 1 2.5 2.5 1-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1 1-2.5zM4 17l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7.7-1.8z"
    />

    <!-- Users -->
    <path
      v-else-if="name === 'users'"
      d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm14 14v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75"
    />

    <!-- Subscriptions / Credit Card -->
    <path
      v-else-if="name === 'subscriptions' || name === 'credit-card'"
      d="M2 5h20a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2zm0 5h20 M6 15h4"
    />

    <!-- AI Models / Chip / CPU -->
    <path
      v-else-if="name === 'models' || name === 'cpu'"
      d="M4 4h16v16H4V4zm5-2v2m6-2v2m-6 16v2m6-2v2M2 9h2m-2 6h2m16-6h2m-2 6h2M9 9h6v6H9V9z"
    />

    <!-- Settings / Sliders -->
    <path
      v-else-if="name === 'settings'"
      d="M4 21v-7m0-4V3m8 18v-9m0-4V3m8 18v-5m0-4V3M1 14h6m2-6h6m2 8h6"
    />

    <!-- Analytics / Bar Chart -->
    <path
      v-else-if="name === 'analytics'"
      d="M18 20V10m-6 10V4M6 20v-6"
    />

    <!-- Sidebar Toggle -->
    <path
      v-else-if="name === 'sidebar-toggle'"
      d="M3 4h18v16H3V4zm6 0v16M15 10l-2 2 2 2"
    />

    <!-- Chat Toggle / Panel -->
    <path
      v-else-if="name === 'chat-toggle'"
      d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
    />

    <!-- Sun (Light Mode) -->
    <path
      v-else-if="name === 'sun'"
      d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z"
    />

    <!-- Moon (Dark Mode) -->
    <path
      v-else-if="name === 'moon'"
      d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
    />

    <!-- Search -->
    <path
      v-else-if="name === 'search'"
      d="M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm10 2-4.35-4.35"
    />

    <!-- Chevron Down -->
    <path
      v-else-if="name === 'chevron-down'"
      d="m6 9 6 6 6-6"
    />

    <!-- Chevron Right -->
    <path
      v-else-if="name === 'chevron-right'"
      d="m9 18 6-6-6-6"
    />

    <!-- Close / X -->
    <path
      v-else-if="name === 'close' || name === 'x'"
      d="M18 6 6 18M6 6l12 12"
    />

    <!-- Send -->
    <path
      v-else-if="name === 'send'"
      d="m22 2-7 20-4-9-9-4 20-7zM22 2 11 13"
    />

    <!-- Code -->
    <path
      v-else-if="name === 'code'"
      d="m16 18 6-6-6-6M8 6l-6 6 6 6"
    />

    <!-- File / Tab -->
    <path
      v-else-if="name === 'file'"
      d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6"
    />

    <!-- Trash / Clear -->
    <path
      v-else-if="name === 'trash'"
      d="M3 6h18m-2 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
    />

    <!-- Fallback circle -->
    <circle v-else cx="12" cy="12" r="9" />
  </svg>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true,
  },
  size: {
    type: [Number, String],
    default: 16,
  },
  strokeWidth: {
    type: [Number, String],
    default: 1.8,
  },
})
</script>

<style scoped>
.svg-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
  transition: transform var(--transition-fast), stroke var(--transition-fast);
}
</style>
