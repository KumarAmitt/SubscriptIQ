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

    <!-- Database / Schema -->
    <path
      v-else-if="name === 'database'"
      d="M3 5c0-1.66 4.03-3 9-3s9 1.34 9 3-4.03 3-9 3-9-1.34-9-3zm0 7c0 1.66 4.03 3 9 3s9-1.34 9-3V5M3 19c0 1.66 4.03 3 9 3s9-1.34 9-3v-7"
    />

    <!-- Book / Examples -->
    <path
      v-else-if="name === 'book' || name === 'examples'"
      d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 0 4 22z"
    />

    <!-- Terminal / Logs -->
    <path
      v-else-if="name === 'terminal' || name === 'logs'"
      d="m4 17 6-6-6-6m8 14h8"
    />

    <!-- Lock / Guardrails -->
    <path
      v-else-if="name === 'lock' || name === 'guardrails'"
      d="M7 11V7a5 5 0 0 1 10 0v4m-12 0h14a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2z"
    />

    <!-- Play / Run -->
    <path
      v-else-if="name === 'play'"
      d="m5 3 14 9-14 9V3z"
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

    <!-- Chevron Up -->
    <path
      v-else-if="name === 'chevron-up'"
      d="m18 15-6-6-6 6"
    />

    <!-- Chevron Right -->
    <path
      v-else-if="name === 'chevron-right'"
      d="m9 18 6-6-6-6"
    />

    <!-- Plus / Add -->
    <path
      v-else-if="name === 'plus' || name === 'add'"
      d="M12 5v14M5 12h14"
    />

    <!-- Microphone / Voice -->
    <path
      v-else-if="name === 'mic' || name === 'microphone'"
      d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z M19 10v2a7 7 0 0 1-14 0v-2 M12 19v4 M8 23h8"
    />

    <!-- Arrow Right -->
    <path
      v-else-if="name === 'arrow-right'"
      d="M5 12h14M12 5l7 7-7 7"
    />

    <!-- Pin (Outline) -->
    <path
      v-else-if="name === 'pin'"
      d="M12 17v5M5 17h14v-1.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v4.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V17z"
    />

    <!-- Pin Filled (Active Pinned State) -->
    <path
      v-else-if="name === 'pin-filled'"
      fill="currentColor"
      d="M12 17v5M5 17h14v-1.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v4.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V17z"
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

    <!-- Download / Export -->
    <path
      v-else-if="name === 'download' || name === 'export'"
      d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4 M7 10l5 5 5-5 M12 15V3"
    />

    <!-- Table -->
    <path
      v-else-if="name === 'table'"
      d="M3 3h18v18H3V3zm0 6h18M3 15h18M9 3v18M15 3v18"
    />

    <!-- Info / Help Circle -->
    <path
      v-else-if="name === 'info' || name === 'help-circle'"
      d="M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M12 16v-4 M12 8h.01"
    />

    <!-- Check Circle / Success -->
    <path
      v-else-if="name === 'check-circle' || name === 'success'"
      d="M22 11.08V12a10 10 0 1 1-5.93-9.14 M22 4 12 14.01l-3-3"
    />

    <!-- Zap / Fast -->
    <path
      v-else-if="name === 'zap' || name === 'lightning'"
      d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"
    />

    <!-- Target / Precision -->
    <path
      v-else-if="name === 'target'"
      d="M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M12 18a6 6 0 1 0 0-12 6 6 0 0 0 0 12z M12 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"
    />

    <!-- Trending Up / Growth -->
    <path
      v-else-if="name === 'trending-up'"
      d="m23 6-9.5 9.5-5-5L1 18 M17 6h6v6"
    />

    <!-- Alert Triangle / Warning -->
    <path
      v-else-if="name === 'alert-triangle' || name === 'warning'"
      d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3z M12 9v4 M12 17h.01"
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
