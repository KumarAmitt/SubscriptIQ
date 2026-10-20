<template>
  <div class="dashboard-view">
    <!-- View Header & Action Bar -->
    <div class="view-header">
      <div class="header-titles">
        <h1 class="view-title">Subscription Overview</h1>
        <p class="view-subtitle">AI-assisted telemetry, license optimization, and contract forecasts</p>
      </div>

      <div class="header-actions">
        <div class="time-filter-pill font-mono">
          <button class="filter-btn active">Month</button>
          <button class="filter-btn">Quarter</button>
          <button class="filter-btn">Year</button>
        </div>
        <button class="primary-ai-btn" @click="triggerAiAudit">
          <Icon name="sparkles" :size="13" />
          <span>Run AI Cost Audit</span>
        </button>
      </div>
    </div>

    <!-- AI Insights Highlight Banner -->
    <div class="ai-banner">
      <div class="banner-badge">
        <Icon name="sparkles" :size="13" />
        <span>COPILOT INTELLIGENCE</span>
      </div>
      <div class="banner-content">
        <h3 class="banner-heading">3 Underutilized SaaS Seats Detected</h3>
        <p class="banner-desc">
          AI telemetry identified 12 dormant Figma and Notion seats over the last 45 days.
          Downgrading unassigned tiers would save an estimated <strong>$340/month</strong>.
        </p>
      </div>
      <div class="banner-actions">
        <button class="banner-action-btn primary" @click="askCopilot('Help me optimize the 3 underutilized SaaS tools')">
          Optimize Now
        </button>
        <button class="banner-action-btn secondary" @click="dismissBanner">
          Dismiss
        </button>
      </div>
    </div>

    <!-- KPI Metric Cards Grid -->
    <div class="kpi-grid">
      <div class="kpi-card" v-for="kpi in kpiCards" :key="kpi.label">
        <div class="kpi-header">
          <span class="kpi-label">{{ kpi.label }}</span>
          <span class="kpi-badge" :class="kpi.badgeClass">{{ kpi.badge }}</span>
        </div>
        <div class="kpi-value font-mono">{{ kpi.value }}</div>
        <div class="kpi-footer">
          <span class="kpi-trend" :class="kpi.trendClass">{{ kpi.trend }}</span>
          <span class="kpi-subtext">{{ kpi.subtext }}</span>
        </div>
      </div>
    </div>

    <!-- Subscriptions Table Section -->
    <div class="table-container-card">
      <div class="table-toolbar">
        <div class="toolbar-title-group">
          <h2 class="table-title">Tracked Subscriptions</h2>
          <span class="counter-tag font-mono">{{ filteredSubscriptions.length }} tools</span>
        </div>

        <div class="table-search-group">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Filter subscriptions..."
            class="table-search-input"
          />
        </div>
      </div>

      <div class="table-responsive">
        <table class="editor-table">
          <thead>
            <tr>
              <th>Service / Tool</th>
              <th>Category</th>
              <th>Seats / Utilization</th>
              <th>Monthly Spend</th>
              <th>Renewal Date</th>
              <th>Status</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sub in filteredSubscriptions" :key="sub.id" class="table-row">
              <td class="tool-cell">
                <div class="tool-icon-box" :style="{ backgroundColor: sub.color + '22', color: sub.color }">
                  {{ sub.abbr }}
                </div>
                <div class="tool-info">
                  <span class="tool-name">{{ sub.name }}</span>
                  <span class="tool-tier font-mono">{{ sub.tier }}</span>
                </div>
              </td>
              <td>
                <span class="category-pill">{{ sub.category }}</span>
              </td>
              <td>
                <div class="utilization-cell">
                  <div class="util-text font-mono">
                    <span>{{ sub.activeSeats }}/{{ sub.totalSeats }} seats</span>
                    <span class="percent">({{ sub.utilization }}%)</span>
                  </div>
                  <div class="progress-track">
                    <div
                      class="progress-fill"
                      :style="{
                        width: sub.utilization + '%',
                        backgroundColor: sub.utilization > 75 ? 'var(--success)' : sub.utilization > 40 ? 'var(--warning)' : 'var(--danger)'
                      }"
                    ></div>
                  </div>
                </div>
              </td>
              <td class="font-mono price-cell">
                ${{ sub.monthlyCost }}<span class="per-mo">/mo</span>
              </td>
              <td class="font-mono text-muted date-cell">
                {{ sub.renewalDate }}
              </td>
              <td>
                <span class="status-pill" :class="sub.statusClass">
                  {{ sub.status }}
                </span>
              </td>
              <td class="text-right">
                <button class="row-action-btn" @click="askCopilot(`Analyze ${sub.name} subscription metrics and contract terms`)">
                  <Icon name="sparkles" :size="12" />
                  <span>Audit</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useUIStore } from '@/stores/ui'
import Icon from '@/components/common/Icon.vue'

const chatStore = useChatStore()
const uiStore = useUIStore()

const searchQuery = ref('')

const kpiCards = ref([
  {
    label: 'Total Monthly Spend',
    value: '$14,840',
    badge: 'MRR',
    badgeClass: 'neutral',
    trend: '+3.2%',
    trendClass: 'warning',
    subtext: 'vs last month',
  },
  {
    label: 'AI Cost Optimizations',
    value: '$1,380',
    badge: 'Savings',
    badgeClass: 'success',
    trend: '9.3%',
    trendClass: 'positive',
    subtext: 'potential reclaim',
  },
  {
    label: 'Active Licenses',
    value: '42 / 48',
    badge: 'Seats',
    badgeClass: 'info',
    trend: '87.5%',
    trendClass: 'neutral',
    subtext: 'overall utilization',
  },
  {
    label: 'Upcoming Renewals',
    value: '3 Tools',
    badge: '14 Days',
    badgeClass: 'warning',
    trend: '$830',
    trendClass: 'neutral',
    subtext: 'total contract value',
  },
])

const subscriptions = ref([
  {
    id: 1,
    name: 'GitHub Enterprise',
    abbr: 'GH',
    color: '#6366f1',
    tier: 'Team Pro • 45 seats',
    category: 'Engineering',
    activeSeats: 43,
    totalSeats: 45,
    utilization: 95,
    monthlyCost: '945.00',
    renewalDate: 'Oct 28, 2026',
    status: 'Optimal',
    statusClass: 'optimal',
  },
  {
    id: 2,
    name: 'OpenAI Enterprise API',
    abbr: 'OA',
    color: '#10b981',
    tier: 'Usage Tier 4',
    category: 'AI Infrastructure',
    activeSeats: 18,
    totalSeats: 20,
    utilization: 90,
    monthlyCost: '4,200.00',
    renewalDate: 'Nov 01, 2026',
    status: 'High Load',
    statusClass: 'active',
  },
  {
    id: 3,
    name: 'Figma Organization',
    abbr: 'FG',
    color: '#ec4899',
    tier: 'Design Team Tier',
    category: 'Product Design',
    activeSeats: 8,
    totalSeats: 16,
    utilization: 50,
    monthlyCost: '720.00',
    renewalDate: 'Nov 12, 2026',
    status: 'Underutilized',
    statusClass: 'warning',
  },
  {
    id: 4,
    name: 'Datadog Pro APM',
    abbr: 'DD',
    color: '#f59e0b',
    tier: 'Infrastructure Hosts',
    category: 'DevOps / Observability',
    activeSeats: 14,
    totalSeats: 15,
    utilization: 93,
    monthlyCost: '2,400.00',
    renewalDate: 'Nov 20, 2026',
    status: 'Optimal',
    statusClass: 'optimal',
  },
  {
    id: 5,
    name: 'Loom Enterprise',
    abbr: 'LM',
    color: '#38bdf8',
    tier: 'Video Workspace',
    category: 'Collaboration',
    activeSeats: 6,
    totalSeats: 25,
    utilization: 24,
    monthlyCost: '350.00',
    renewalDate: 'Nov 04, 2026',
    status: 'Overprovisioned',
    statusClass: 'danger',
  },
  {
    id: 6,
    name: 'Notion AI Workspace',
    abbr: 'NT',
    color: '#a855f7',
    tier: 'Plus + AI Addon',
    category: 'Productivity',
    activeSeats: 22,
    totalSeats: 30,
    utilization: 73,
    monthlyCost: '480.00',
    renewalDate: 'Dec 01, 2026',
    status: 'Healthy',
    statusClass: 'optimal',
  },
])

const filteredSubscriptions = computed(() => {
  if (!searchQuery.value.trim()) return subscriptions.value
  const q = searchQuery.value.toLowerCase()
  return subscriptions.value.filter(
    (s) =>
      s.name.toLowerCase().includes(q) ||
      s.category.toLowerCase().includes(q) ||
      s.status.toLowerCase().includes(q)
  )
})

function askCopilot(prompt) {
  if (uiStore.isChatCollapsed) {
    uiStore.toggleChat()
  }
  chatStore.sendMessage(prompt)
}

function triggerAiAudit() {
  askCopilot('Perform a complete subscription telemetry audit and identify reclaimable seats.')
}

function dismissBanner(e) {
  e.target.closest('.ai-banner').style.display = 'none'
}
</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Header */
.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.view-title {
  font-size: var(--text-lg);
  font-weight: var(--font-weight-semibold);
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.view-subtitle {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: 2px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-filter-pill {
  display: flex;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 2px;
}

.filter-btn {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
  color: var(--text-secondary);
}

.filter-btn.active {
  background-color: var(--bg-card);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.primary-ai-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: var(--radius-md);
  background: var(--accent);
  color: #ffffff;
  font-size: var(--text-xs);
  font-weight: var(--font-weight-medium);
  box-shadow: var(--accent-glow);
  transition: all var(--transition-fast);
}

.primary-ai-btn:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

/* AI Banner */
.ai-banner {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  position: relative;
  overflow: hidden;
}

.ai-banner::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: var(--accent-gradient);
}

.banner-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  font-family: var(--font-mono);
  font-weight: var(--font-weight-semibold);
  color: var(--accent);
  background-color: var(--accent-light);
  padding: 2px 7px;
  border-radius: var(--radius-full);
}

.banner-content {
  flex: 1;
}

.banner-heading {
  font-size: var(--text-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin-bottom: 2px;
}

.banner-desc {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  line-height: 1.4;
}

.banner-desc strong {
  color: var(--success);
}

.banner-actions {
  display: flex;
  gap: 8px;
}

.banner-action-btn {
  font-size: var(--text-xs);
  font-weight: var(--font-weight-medium);
  padding: 6px 12px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.banner-action-btn.primary {
  background-color: var(--accent);
  color: #ffffff;
}

.banner-action-btn.primary:hover {
  background-color: var(--accent-hover);
}

.banner-action-btn.secondary {
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.banner-action-btn.secondary:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 12px;
}

.kpi-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color var(--transition-fast);
}

.kpi-card:hover {
  border-color: var(--border-highlight);
}

.kpi-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kpi-label {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.kpi-badge {
  font-size: 9.5px;
  font-family: var(--font-mono);
  padding: 1px 5px;
  border-radius: 3px;
}

.kpi-badge.success { background: var(--success-bg); color: var(--success); }
.kpi-badge.warning { background: var(--warning-bg); color: var(--warning); }
.kpi-badge.info { background: var(--info-bg); color: var(--info); }
.kpi-badge.neutral { background: var(--bg-tertiary); color: var(--text-secondary); }

.kpi-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.kpi-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
}

.kpi-trend {
  font-weight: var(--font-weight-medium);
  font-family: var(--font-mono);
}

.kpi-trend.positive { color: var(--success); }
.kpi-trend.warning { color: var(--warning); }
.kpi-trend.neutral { color: var(--text-secondary); }

.kpi-subtext {
  color: var(--text-muted);
}

/* Table Section */
.table-container-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.table-toolbar {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.toolbar-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-title {
  font-size: var(--text-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.counter-tag {
  font-size: 10px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  padding: 1px 6px;
  border-radius: var(--radius-full);
  color: var(--text-muted);
}

.table-search-input {
  font-size: 11px;
  padding: 4px 10px;
  width: 200px;
}

.table-responsive {
  overflow-x: auto;
}

.editor-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: var(--text-xs);
}

.editor-table th {
  padding: 8px 14px;
  font-size: 11px;
  font-weight: var(--font-weight-medium);
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
}

.editor-table td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  vertical-align: middle;
}

.table-row:hover td {
  background-color: var(--bg-hover);
}

.tool-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tool-icon-box {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  font-family: var(--font-mono);
}

.tool-info {
  display: flex;
  flex-direction: column;
}

.tool-name {
  font-size: var(--text-xs);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.tool-tier {
  font-size: 10px;
  color: var(--text-muted);
}

.category-pill {
  font-size: 10.5px;
  background-color: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}

.utilization-cell {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 130px;
}

.util-text {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--text-muted);
}

.progress-track {
  height: 4px;
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
}

.price-cell {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--text-primary);
}

.per-mo {
  font-size: 10px;
  color: var(--text-muted);
  font-weight: normal;
}

.status-pill {
  font-size: 10px;
  font-family: var(--font-mono);
  padding: 2px 6px;
  border-radius: var(--radius-full);
}

.status-pill.optimal { background: var(--success-bg); color: var(--success); }
.status-pill.active { background: var(--info-bg); color: var(--info); }
.status-pill.warning { background: var(--warning-bg); color: var(--warning); }
.status-pill.danger { background: var(--danger-bg); color: var(--danger); }

.row-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--accent);
}

.row-action-btn:hover {
  background-color: var(--accent-light);
  border-color: var(--accent);
}

.text-right {
  text-align: right;
}
</style>
