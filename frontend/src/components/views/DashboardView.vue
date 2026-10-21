<template>
  <div class="dashboard-view">
    <!-- View Header & Action Bar -->
    <div class="view-header">
      <div class="header-titles">
        <h1 class="view-title">Subscription Intelligence & Spend Telemetry</h1>
        <p class="view-subtitle">Live SaaS contracts, seat telemetry, and automated AI cost optimization</p>
      </div>

      <div class="header-actions">
        <button class="primary-ai-btn" @click="triggerAiAudit">
          <Icon name="sparkles" :size="13" />
          <span>Run AI Cost Audit</span>
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

    <!-- AI Cost Optimization Opportunities Section (Live Detections) -->
    <div v-if="recommendations.length > 0" class="recommendations-container">
      <div class="recs-header">
        <div class="recs-title-group">
          <div class="ai-shield-pill font-mono">
            <Icon name="sparkles" :size="12" />
            <span>AI COST AUDIT OPPORTUNITIES</span>
          </div>
          <span class="recs-subtitle">Active telemetry detections with verified return on investment</span>
        </div>
        <button class="recs-audit-all-btn" @click="triggerAiAudit">
          <Icon name="sparkles" :size="12" />
          <span>Audit All Opportunities</span>
        </button>
      </div>

      <div class="recs-grid">
        <div v-for="rec in recommendations" :key="rec.id" class="rec-card">
          <div class="rec-card-top">
            <span class="rec-type-badge font-mono">{{ formatRecType(rec.recommendation_type) }}</span>
            <span class="rec-savings font-mono">+{{ currencySymbol }}{{ Number(rec.estimated_monthly_savings).toLocaleString('en-IN') }}/mo</span>
          </div>
          <h4 class="rec-product">{{ rec.product_name }}</h4>
          <p class="rec-desc">{{ rec.description }}</p>
          <div class="rec-footer">
            <span class="rec-confidence font-mono">
              <span class="conf-dot"></span>
              {{ Math.round(rec.confidence_score * 100) }}% confidence
            </span>
            <button class="rec-action-btn" @click="askChat(`Explain recommendation for ${rec.product_name} and estimate annual cost impact`)">
              <span>Investigate</span>
              <Icon name="arrow-right" :size="11" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Analytics Inquiries Carousel / Chips -->
    <div class="quick-inquiries-bar">
      <div class="quick-title font-mono">
        <Icon name="analytics" :size="13" />
        <span>QUICK NL QUERIES:</span>
      </div>
      <div class="chips-scroll">
        <button
          v-for="chip in quickChips"
          :key="chip.label"
          class="prompt-chip"
          @click="askChat(chip.prompt)"
        >
          <span class="chip-icon">{{ chip.icon }}</span>
          <span class="chip-text">{{ chip.label }}</span>
          <span class="chip-badge font-mono">{{ chip.type }}</span>
        </button>
      </div>
    </div>

    <!-- Subscriptions Table Section -->
    <div class="table-container-card">
      <div class="table-toolbar">
        <div class="toolbar-title-group">
          <h2 class="table-title">Tracked Enterprise Subscriptions</h2>
          <span class="counter-tag font-mono">{{ filteredSubscriptions.length }} tools</span>
        </div>

        <div class="table-controls-group">
          <!-- Category Filter Pills -->
          <div class="category-filter-pills">
            <button
              v-for="cat in availableCategories"
              :key="cat"
              class="cat-pill"
              :class="{ active: selectedCategory === cat }"
              @click="selectedCategory = cat"
            >
              {{ cat }}
            </button>
          </div>

          <!-- Search Input -->
          <div class="table-search-group">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search subscriptions or category..."
              class="table-search-input"
            />
          </div>
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
                {{ currencySymbol }}{{ sub.monthlyCost }}<span class="per-mo">/mo</span>
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
                <button class="row-action-btn" @click="askChat(`Audit ${sub.name} subscription metrics: assigned users, cost per user, unallocated seats, and dormant waste`)">
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
import { ref, computed, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useUIStore } from '@/stores/ui'
import Icon from '@/components/common/Icon.vue'

const chatStore = useChatStore()
const uiStore = useUIStore()

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const currencySymbol = ref(import.meta.env.VITE_CURRENCY_SYMBOL || '₹')

const searchQuery = ref('')
const selectedCategory = ref('All')
const isLoading = ref(true)

const kpiCards = ref([
  {
    label: 'Total Monthly Spend',
    value: `${currencySymbol.value}62,85,500`,
    badge: 'MRR',
    badgeClass: 'neutral',
    trend: '+4.1%',
    trendClass: 'warning',
    subtext: 'vs last month',
  },
  {
    label: 'AI Cost Optimizations',
    value: `${currencySymbol.value}2,25,000`,
    badge: 'Savings',
    badgeClass: 'success',
    trend: '9.4%',
    trendClass: 'positive',
    subtext: 'potential reclaim',
  },
  {
    label: 'Dormant License Seats',
    value: '290 Seats',
    badge: 'Idle',
    badgeClass: 'danger',
    trend: '19.3%',
    trendClass: 'warning',
    subtext: 'inactive > 30 days',
  },
  {
    label: 'Upcoming Renewals',
    value: '2 Tools',
    badge: '14 Days',
    badgeClass: 'warning',
    trend: `${currencySymbol.value}8,50,000`,
    trendClass: 'neutral',
    subtext: 'approaching renewal',
  },
])

const subscriptions = ref([])
const recommendations = ref([])

const quickChips = [
  { icon: '📊', label: 'Top 5 Subscriptions by Spend', type: 'AGGREGATE', prompt: 'Top 5 subscriptions by monthly spend' },
  { icon: '⏳', label: 'Renewals Next 30 Days', type: 'TEMPORAL', prompt: 'Which subscriptions renew in the next 30 days?' },
  { icon: '💤', label: 'Dormant Seats per Tool', type: 'JOIN', prompt: 'How many dormant license seats are there per tool?' },
  { icon: '🏢', label: 'Department Spend Breakdown', type: 'JOIN', prompt: 'Total spend and active subscriptions by department' },
  { icon: '📑', label: 'Pending or Overdue Invoices', type: 'SIMPLE', prompt: 'Show all pending or overdue invoices' },
]

const availableCategories = computed(() => {
  const cats = new Set(subscriptions.value.map(s => s.category).filter(Boolean))
  return ['All', ...Array.from(cats)]
})

function formatRecType(type) {
  if (!type) return 'RECOMMENDATION'
  return type.replace(/_/g, ' ').toUpperCase()
}

async function loadDashboardData() {
  try {
    const res = await fetch(`${API_BASE}/dashboard/stats`)
    if (res.ok) {
      const data = await res.json()
      if (data.currency_symbol) {
        currencySymbol.value = data.currency_symbol
      }
      const sym = currencySymbol.value
      if (data.metrics) {
        kpiCards.value[0].value = `${sym}${Number(data.metrics.total_monthly_spend || 0).toLocaleString('en-IN')}`
        kpiCards.value[1].value = `${sym}${Number(data.metrics.projected_monthly_savings || 0).toLocaleString('en-IN')}`
        kpiCards.value[2].value = `${data.metrics.dormant_seats} Seats`
        kpiCards.value[3].value = `${data.metrics.renewals_in_14_days} Tools`
      }
      if (data.subscriptions && data.subscriptions.length > 0) {
        subscriptions.value = data.subscriptions.map(s => ({
          ...s,
          monthlyCost: Number(s.monthly_cost).toLocaleString('en-IN'),
          renewalDate: s.renewal,
          statusClass: s.status === 'active' ? 'optimal' : s.status === 'under_review' ? 'warning' : 'active'
        }))
      }
      if (data.recommendations && data.recommendations.length > 0) {
        recommendations.value = data.recommendations
      }
    }
  } catch (err) {
    console.warn('Dashboard fetch notice:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})

const filteredSubscriptions = computed(() => {
  let list = subscriptions.value

  if (selectedCategory.value !== 'All') {
    list = list.filter(s => s.category === selectedCategory.value)
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        s.category.toLowerCase().includes(q) ||
        s.status.toLowerCase().includes(q)
    )
  }

  return list
})

function askChat(prompt) {
  if (uiStore.isChatCollapsed) {
    uiStore.toggleChat()
  }
  chatStore.sendMessage(prompt)
}

function triggerAiAudit() {
  askChat('Audit subscriptions with dormant seats and cost optimization recommendations')
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

.primary-ai-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  background: var(--btn-primary-gradient);
  border: 1px solid var(--btn-primary-border);
  color: #ffffff;
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.01em;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.35);
  transition: all var(--transition-fast);
  cursor: pointer;
}

.primary-ai-btn:hover {
  background: var(--btn-primary-gradient-hover);
  border-color: rgba(56, 189, 248, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.45);
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

/* AI Recommendations Opportunities Container */
.recommendations-container {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.05) 0%, rgba(99, 102, 241, 0.04) 100%);
  border: 1px solid rgba(14, 165, 233, 0.25);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.recs-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-shield-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(14, 165, 233, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 3px 8px;
  border-radius: var(--radius-full);
}

.recs-subtitle {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.recs-audit-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: var(--radius-md);
  background: rgba(14, 165, 233, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: #38bdf8;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.recs-audit-all-btn:hover {
  background: rgba(14, 165, 233, 0.25);
  border-color: #38bdf8;
  color: #ffffff;
}

.recs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 10px;
}

.rec-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: all var(--transition-fast);
}

.rec-card:hover {
  border-color: rgba(56, 189, 248, 0.4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.rec-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.rec-type-badge {
  font-size: 9px;
  font-weight: 700;
  color: var(--text-secondary);
  background-color: var(--bg-tertiary);
  padding: 2px 5px;
  border-radius: 3px;
}

.rec-savings {
  font-size: 11px;
  font-weight: 700;
  color: var(--success);
}

.rec-product {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.rec-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.35;
  margin: 0;
  flex: 1;
}

.rec-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
  padding-top: 6px;
  border-top: 1px solid var(--border-subtle);
}

.rec-confidence {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: var(--text-muted);
}

.conf-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: var(--success);
}

.rec-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 600;
  color: #38bdf8;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 3px;
  transition: all var(--transition-fast);
}

.rec-action-btn:hover {
  color: #ffffff;
  background: rgba(56, 189, 248, 0.2);
}

/* Quick NL Inquiries Bar */
.quick-inquiries-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.quick-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10.5px;
  font-weight: 700;
  color: var(--text-muted);
  white-space: nowrap;
}

.chips-scroll {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
}

.chips-scroll::-webkit-scrollbar {
  display: none;
}

.prompt-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  font-size: 11px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  white-space: nowrap;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.prompt-chip:hover {
  background-color: rgba(14, 165, 233, 0.15);
  border-color: rgba(56, 189, 248, 0.4);
  color: #38bdf8;
  transform: translateY(-1px);
}

.chip-icon {
  font-size: 11px;
}

.chip-badge {
  font-size: 8.5px;
  background-color: rgba(255, 255, 255, 0.06);
  padding: 1px 4px;
  border-radius: 3px;
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
  flex-wrap: wrap;
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
  margin: 0;
}

.counter-tag {
  font-size: 10px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  padding: 1px 6px;
  border-radius: var(--radius-full);
  color: var(--text-muted);
}

.table-controls-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.category-filter-pills {
  display: flex;
  align-items: center;
  gap: 4px;
  background-color: var(--bg-tertiary);
  padding: 2px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.cat-pill {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 4px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.cat-pill:hover {
  color: var(--text-primary);
}

.cat-pill.active {
  background-color: var(--bg-card);
  color: #38bdf8;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.table-search-input {
  font-size: 11px;
  padding: 5px 10px;
  width: 220px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  outline: none;
}

.table-search-input:focus {
  border-color: var(--accent);
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
  cursor: pointer;
  transition: all var(--transition-fast);
}

.row-action-btn:hover {
  background-color: var(--accent-light);
  border-color: var(--accent);
  color: #38bdf8;
}

.text-right {
  text-align: right;
}
</style>
