<template>
  <div class="query-analysis-view">
    <!-- State 1: Query In Progress Loading State -->
    <div v-if="chatStore.isTyping" class="analysis-loading-card">
      <div class="loading-spinner-wrap">
        <div class="quantum-spinner"></div>
      </div>
      <div class="loading-text-group">
        <span class="loading-label font-mono">AI PIPELINE EXECUTING</span>
        <h3 class="loading-title">Analyzing query and calculating metrics...</h3>
        <p class="loading-subtitle font-mono">
          Querying SaaS contracts, license allocations, and spend telemetry via LangGraph
        </p>
      </div>
    </div>

    <!-- State 2: Query Result Available (Success or Guardrail Blocked) -->
    <div v-else-if="activeQuery" class="analysis-container">
      <!-- Header & Query Overview -->
      <div class="analysis-header-card">
        <div class="header-top-row">
          <div class="query-title-group">
            <div class="query-icon-pill" :class="{ 'is-blocked': activeQuery.isSuccess === false }">
              <Icon :name="activeQuery.isSuccess === false ? 'lock' : 'sparkles'" :size="16" />
            </div>
            <div>
              <div class="query-meta-tag font-mono">
                {{ activeQuery.isSuccess === false ? 'SECURITY / GUARDRAILS CHECK' : 'CHAT ANALYSIS REPORT' }}
              </div>
              <h1 class="query-title">"{{ activeQuery.query }}"</h1>
            </div>
          </div>

          <!-- Quick Action Buttons -->
          <div class="header-action-group" v-if="activeQuery.rows && activeQuery.rows.length > 0">
            <button class="action-btn" @click="exportCSV" title="Export as CSV file">
              <Icon name="download" :size="13" />
              <span>Export CSV</span>
            </button>
            <button class="action-btn" @click="exportJSON" title="Export as JSON file">
              <Icon name="code" :size="13" />
              <span>Export JSON</span>
            </button>
            <button class="action-btn" @click="copyTableData" title="Copy dataset to clipboard">
              <Icon name="file" :size="13" />
              <span>{{ isCopied ? 'Copied!' : 'Copy Table' }}</span>
            </button>
          </div>
        </div>

        <!-- Telemetry Badges Strip -->
        <div class="telemetry-badges-strip font-mono">
          <div class="telemetry-item">
            <span class="telemetry-label">Status:</span>
            <span
              class="status-badge"
              :class="activeQuery.isSuccess === false ? 'badge-blocked' : 'badge-success'"
            >
              {{ activeQuery.isSuccess === false ? 'Blocked / Notice' : 'Success' }}
            </span>
          </div>

          <div class="telemetry-divider"></div>

          <div class="telemetry-item">
            <span class="telemetry-label">Records:</span>
            <span class="telemetry-val highlight">{{ activeQuery.rowCount || 0 }} rows</span>
          </div>

          <div class="telemetry-divider" v-if="activeQuery.latency"></div>

          <div class="telemetry-item" v-if="activeQuery.latency">
            <span class="telemetry-label">Latency:</span>
            <span class="telemetry-val">⚡ {{ activeQuery.latency }}ms</span>
          </div>

          <div class="telemetry-divider" v-if="activeQuery.queryType"></div>

          <div class="telemetry-item" v-if="activeQuery.queryType">
            <span class="telemetry-label">Type:</span>
            <span class="type-pill">{{ activeQuery.queryType }}</span>
          </div>

          <div class="telemetry-divider" v-if="activeQuery.modelUsed"></div>

          <div class="telemetry-item" v-if="activeQuery.modelUsed">
            <span class="telemetry-label">Model:</span>
            <span class="telemetry-val">{{ formatModelName(activeQuery.modelUsed) }}</span>
          </div>

          <div class="telemetry-divider" v-if="activeQuery.timestamp"></div>

          <div class="telemetry-item" v-if="activeQuery.timestamp">
            <span class="telemetry-label">Time:</span>
            <span class="telemetry-val">{{ activeQuery.timestamp }}</span>
          </div>
        </div>
      </div>

      <!-- Error / Guardrail Blocked Notice Banner -->
      <div v-if="activeQuery.isSuccess === false" class="guardrail-alert-card">
        <div class="alert-icon-wrap">
          <Icon name="lock" :size="18" />
        </div>
        <div class="alert-text-wrap">
          <h3 class="alert-title">Query Execution Restricted</h3>
          <p class="alert-body">{{ activeQuery.error || activeQuery.nlSummary }}</p>
          <p class="alert-hint font-mono">
            SubscriptIQ operates in strict read-only mode to safeguard corporate financial data. Only analytical SELECT queries are supported.
          </p>
        </div>
      </div>

      <!-- Key Insights Summary Callout -->
      <div v-if="activeQuery.nlSummary && activeQuery.isSuccess !== false" class="insight-summary-card">
        <div class="insight-beacon">
          <Icon name="sparkles" :size="16" />
        </div>
        <div class="insight-text-column">
          <h2 class="insight-heading">Key Analytical Takeaways</h2>
          <div class="insight-body" v-html="formatInsightText(activeQuery.nlSummary)"></div>
          <p v-if="activeQuery.explanation" class="insight-explanation font-mono">
            ℹ️ {{ activeQuery.explanation }}
          </p>
        </div>
      </div>

      <!-- Visual Analytics Chart & Summary KPI Cards -->
      <div
        v-if="effectiveChart && effectiveChart.labels && effectiveChart.labels.length"
        class="visual-analytics-grid"
      >
        <!-- Chart Breakdown (Supports interactive Donut/Pie + Proportional Bars) -->
        <div class="chart-main-card">
          <div class="chart-header">
            <div class="chart-header-title">
              <Icon name="analytics" :size="14" />
              <span>{{ effectiveChart.title || 'Distribution Breakdown' }}</span>
            </div>
            <div class="chart-header-badges">
              <span v-if="isDoughnutOrPie" class="chart-type-pill font-mono">DOUGHNUT / PIE</span>
              <span class="chart-metric-badge font-mono">{{ effectiveChart.labels.length }} metrics</span>
            </div>
          </div>

          <!-- Split Layout: SVG Donut Visual on Left, Bars & Legend on Right -->
          <div class="chart-layout-body" :class="{ 'with-donut': isDoughnutOrPie && donutSegments.length > 0 }">
            <!-- SVG Donut Chart Ring -->
            <div v-if="isDoughnutOrPie && donutSegments.length > 0" class="donut-chart-wrapper">
              <div class="donut-svg-container">
                <svg class="donut-svg" viewBox="0 0 140 140">
                  <circle
                    class="donut-bg-ring"
                    cx="70"
                    cy="70"
                    r="50"
                    fill="transparent"
                    stroke-width="16"
                  />
                  <circle
                    v-for="(seg, sIdx) in donutSegments"
                    :key="sIdx"
                    class="donut-segment"
                    cx="70"
                    cy="70"
                    r="50"
                    fill="transparent"
                    stroke-width="16"
                    :stroke="seg.color"
                    :stroke-dasharray="seg.strokeDasharray"
                    :stroke-dashoffset="seg.strokeDashoffset"
                  />
                </svg>
                <div class="donut-center-content font-mono">
                  <span class="donut-center-tag">{{ donutCenterLabel }}</span>
                  <span class="donut-center-main">{{ donutCenterValue }}</span>
                  <span class="donut-center-sub" v-if="recommendationSummary">RECLAIM</span>
                  <span class="donut-center-sub" v-else-if="auditSummary">OPTIMIZATION</span>
                  <span class="donut-center-sub" v-else>ALLOCATION</span>
                </div>
              </div>
            </div>

            <!-- Proportional Bars Container -->
            <div class="chart-bars-container">
              <div
                v-for="(label, idx) in effectiveChart.labels"
                :key="idx"
                class="chart-bar-item font-mono"
              >
                <div class="bar-info-row">
                  <div class="bar-label-with-dot">
                    <span class="legend-color-dot" :style="{ backgroundColor: getBarColor(idx) }"></span>
                    <span class="bar-item-label" :title="label">{{ label }}</span>
                  </div>
                  <div class="bar-value-with-pct">
                    <span class="bar-item-value">{{ formatChartVal(effectiveChart.values[idx]) }}</span>
                    <span class="bar-item-pct" v-if="donutSegments[idx]">({{ donutSegments[idx].pct }}%)</span>
                  </div>
                </div>
                <div class="bar-track-wrap">
                  <div
                    class="bar-fill-dynamic"
                    :style="{
                      width: calculatePercentage(effectiveChart.values[idx], effectiveChart.values) + '%',
                      backgroundColor: getBarColor(idx)
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Meaningful Numerical & Business KPI Cards -->
        <div class="kpi-side-column">
          <!-- 1. Dedicated Subscription Audit KPI Cards -->
          <template v-if="auditSummary">
            <div class="summary-kpi-card">
              <span class="kpi-label">Monthly Subscription Cost</span>
              <span class="kpi-number text-accent">{{ currencySymbol }}{{ formatNumber(auditSummary.monthlyCost) }}</span>
              <span class="kpi-subtext">Capacity: {{ auditSummary.totalSeats }} licensed seats ({{ currencySymbol }}{{ formatNumber(auditSummary.costPerSeat) }}/seat)</span>
            </div>

            <div class="summary-kpi-card">
              <span class="kpi-label">Cost Per Assigned User</span>
              <span class="kpi-number text-highlight">{{ currencySymbol }}{{ formatNumber(auditSummary.costPerUser) }}</span>
              <span class="kpi-subtext">{{ auditSummary.assignedUsers }} active employees assigned</span>
            </div>

            <div class="summary-kpi-card">
              <span class="kpi-label">Headcount & Capacity</span>
              <span class="kpi-number">{{ auditSummary.assignedUsers }} / {{ auditSummary.totalSeats }}</span>
              <span class="kpi-subtext">{{ auditSummary.allocationRate }}% allocated ({{ auditSummary.unallocatedSeats }} idle seats)</span>
            </div>

            <div class="summary-kpi-card audit-waste-card">
              <span class="kpi-label text-warning">Recoverable Waste</span>
              <span class="kpi-number text-warning">{{ currencySymbol }}{{ formatNumber(auditSummary.totalWaste) }}<span class="subtext-unit">/mo</span></span>
              <span class="kpi-subtext text-warning">
                {{ auditSummary.optimizationPct }}% optimizable ({{ auditSummary.dormantSeats }} dormant, {{ auditSummary.unallocatedSeats }} idle)
              </span>
            </div>
          </template>

          <!-- 2. Dedicated Cost Optimization & Recommendation KPI Cards -->
          <template v-else-if="recommendationSummary">
            <div class="summary-kpi-card rec-highlight-card">
              <span class="kpi-label">Projected Annual Savings</span>
              <span class="kpi-number text-accent font-mono">+{{ currencySymbol }}{{ formatNumber(recommendationSummary.annualSavings) }}</span>
              <span class="kpi-subtext text-accent">+{{ currencySymbol }}{{ formatNumber(recommendationSummary.monthlySavings) }}/mo recurring reclaim</span>
            </div>

            <div class="summary-kpi-card">
              <span class="kpi-label">Current Contract Spend</span>
              <span class="kpi-number text-highlight font-mono">{{ currencySymbol }}{{ formatNumber(recommendationSummary.annualCost) }}</span>
              <span class="kpi-subtext">{{ currencySymbol }}{{ formatNumber(recommendationSummary.monthlyCost) }}/month current baseline</span>
            </div>

            <div class="summary-kpi-card">
              <span class="kpi-label">Optimization Strategy</span>
              <span class="kpi-number text-strategy font-mono">{{ recommendationSummary.recType }}</span>
              <span class="kpi-subtext" :title="recommendationSummary.description">{{ recommendationSummary.description.length > 55 ? recommendationSummary.description.substring(0, 55) + '...' : recommendationSummary.description }}</span>
            </div>

            <div class="summary-kpi-card">
              <span class="kpi-label">AI Telemetry Confidence</span>
              <span class="kpi-number text-success font-mono">
                <span class="conf-pulse-dot"></span>
                {{ recommendationSummary.confidenceScore }}% Verified
              </span>
              <span class="kpi-subtext">Telemetry-verified optimization detection</span>
            </div>
          </template>

          <!-- Standard KPI Cards for general queries -->
          <template v-else>
            <!-- 1. Total Volume / Records -->
            <div class="summary-kpi-card">
              <span class="kpi-label">Total Records</span>
              <span class="kpi-number">{{ activeQuery.rows ? activeQuery.rows.length : 0 }}</span>
              <span class="kpi-subtext">{{ datasetLabel }}</span>
            </div>

            <!-- 2. Aggregated Spend / Financial Impact -->
            <div class="summary-kpi-card" v-if="computedTotalValue > 0">
              <span class="kpi-label">Aggregated Spend</span>
              <span class="kpi-number text-accent">{{ currencySymbol }}{{ formatNumber(computedTotalValue) }}</span>
              <span class="kpi-subtext">Avg: {{ currencySymbol }}{{ formatNumber(averageSpendValue) }} / service</span>
            </div>

            <!-- 3. Highest Cost Item -->
            <div class="summary-kpi-card" v-if="highestCostItem">
              <span class="kpi-label">Highest Expense</span>
              <span class="kpi-number text-highlight" :title="highestCostItem.name">{{ highestCostItem.name }}</span>
              <span class="kpi-subtext font-mono text-accent">
                {{ currencySymbol }}{{ formatNumber(highestCostItem.val) }}
                <span v-if="computedTotalValue > 0" class="subtext-pct">({{ Math.round((highestCostItem.val / computedTotalValue) * 100) }}% of total)</span>
              </span>
            </div>

            <!-- 4. Lowest Cost Item (When more than 1 service) -->
            <div class="summary-kpi-card" v-if="lowestCostItem && highestCostItem && lowestCostItem.name !== highestCostItem.name">
              <span class="kpi-label">Lowest Expense</span>
              <span class="kpi-number text-muted-bright" :title="lowestCostItem.name">{{ lowestCostItem.name }}</span>
              <span class="kpi-subtext font-mono text-muted">
                {{ currencySymbol }}{{ formatNumber(lowestCostItem.val) }} (Most cost-effective)
              </span>
            </div>

            <!-- 5. Fallback Top Contributor for non-financial numeric queries -->
            <div class="summary-kpi-card" v-else-if="topNonIdContributor">
              <span class="kpi-label">{{ topNonIdContributor.label }}</span>
              <span class="kpi-number text-highlight">{{ topNonIdContributor.name }}</span>
              <span class="kpi-subtext">{{ formatChartVal(topNonIdContributor.val) }} (Leading)</span>
            </div>
          </template>
        </div>
      </div>

      <!-- In-Depth Full Data Table -->
      <div v-if="activeQuery.rows && activeQuery.rows.length > 0" class="full-table-card">
        <div class="table-toolbar">
          <div class="table-toolbar-left">
            <h3 class="table-card-title">
              <Icon name="table" :size="14" />
              <span>Complete In-Depth Dataset</span>
            </h3>
            <span class="table-rows-counter font-mono">
              Showing {{ pageStartRecord }}–{{ pageEndRecord }} of {{ filteredAndSortedRows.length }} records
            </span>
          </div>

          <div class="table-toolbar-right">
            <!-- Search Filter Input -->
            <div class="search-filter-box">
              <Icon name="search" :size="13" class="search-icon" />
              <input
                v-model="tableSearchQuery"
                type="text"
                placeholder="Search within rows..."
                class="search-input font-mono"
              />
              <button
                v-if="tableSearchQuery"
                class="clear-search-btn"
                @click="tableSearchQuery = ''"
              >
                <Icon name="close" :size="10" />
              </button>
            </div>
          </div>
        </div>

        <!-- Scrollable Table -->
        <div class="table-responsive-scroll">
          <table class="in-depth-data-table font-mono">
            <thead>
              <tr>
                <th class="sno-th">#</th>
                <th
                  v-for="col in activeQuery.columns"
                  :key="col"
                  @click="sortByColumn(col)"
                  class="sortable-th"
                  :class="{ 'is-sorted': sortColumn === col }"
                >
                  <div class="th-content">
                    <span>{{ formatColumnHeader(col) }}</span>
                    <span class="sort-indicator">
                      {{ sortColumn === col ? (sortAsc ? '▲' : '▼') : '↕' }}
                    </span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rIdx) in paginatedRows" :key="rIdx">
                <td class="sno-cell font-mono text-muted">
                  {{ (currentPage - 1) * (pageSize === -1 ? 0 : pageSize) + rIdx + 1 }}
                </td>
                <td v-for="col in activeQuery.columns" :key="col" :class="getCellAlignment(col, row[col])">
                  <!-- Status Column -->
                  <span v-if="isStatusColumn(col)" :class="['status-chip', getStatusClass(row[col])]">
                    {{ row[col] }}
                  </span>
                  <!-- Currency / Numeric Formatted -->
                  <span v-else-if="isCurrencyColumn(col) && isNumeric(row[col])">
                    {{ currencySymbol }}{{ formatNumber(row[col]) }}
                  </span>
                  <!-- Regular Value -->
                  <span v-else>
                    {{ formatCellValue(row[col]) }}
                  </span>
                </td>
              </tr>
              <tr v-if="paginatedRows.length === 0">
                <td :colspan="(activeQuery.columns ? activeQuery.columns.length : 0) + 1" class="empty-search-cell">
                  No records match filter "{{ tableSearchQuery }}"
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Table Pagination Bar -->
        <div v-if="filteredAndSortedRows.length > 40 || totalPages > 1" class="table-pagination-bar font-mono">
          <div class="pagination-info">
            <span>
              Showing <strong class="text-accent">{{ pageStartRecord }}–{{ pageEndRecord }}</strong> of <strong>{{ filteredAndSortedRows.length }}</strong> records
            </span>
          </div>

          <div class="pagination-controls" v-if="totalPages > 1">
            <button
              class="pagination-btn"
              :disabled="currentPage === 1"
              @click="goToPage(1)"
              title="First Page"
            >
              «
            </button>
            <button
              class="pagination-btn"
              :disabled="currentPage === 1"
              @click="goToPage(currentPage - 1)"
              title="Previous Page"
            >
              ‹ Prev
            </button>

            <div class="pagination-page-pills">
              <button
                v-for="p in visiblePages"
                :key="p"
                class="pagination-page-pill"
                :class="{ 'active': p === currentPage }"
                @click="goToPage(p)"
              >
                {{ p }}
              </button>
            </div>

            <button
              class="pagination-btn"
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
              title="Next Page"
            >
              Next ›
            </button>
            <button
              class="pagination-btn"
              :disabled="currentPage === totalPages"
              @click="goToPage(totalPages)"
              title="Last Page"
            >
              »
            </button>
          </div>

          <div class="pagination-size-selector">
            <span class="size-label">Rows per page:</span>
            <select v-model.number="pageSize" class="size-select font-mono">
              <option :value="20">20</option>
              <option :value="40">40</option>
              <option :value="100">100</option>
              <option :value="-1">All</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Fallback when 0 rows returned -->
      <div v-else-if="activeQuery.isSuccess !== false" class="zero-rows-card">
        <div class="zero-rows-icon">
          <Icon name="database" :size="24" />
        </div>
        <h3 class="zero-rows-title">0 Records Returned</h3>
        <p class="zero-rows-desc">
          The query ran successfully, but no matching records were found with the specified parameters.
        </p>
      </div>
    </div>

    <!-- State 3: Empty State (Before Any Query Is Run) -->
    <div v-else class="empty-state-card">
      <div class="empty-icon-wrap">
        <Icon name="analytics" :size="28" />
      </div>
      <h2 class="empty-title">Chat Analysis Workspace</h2>
      <p class="empty-desc">
        Ask a question in the <strong>CHAT ASSISTANT</strong> on the right to automatically generate and explore comprehensive in-depth datasets, key takeaways, and visual charts here.
      </p>
      <div class="empty-quick-prompts">
        <span class="empty-prompts-label">Or click a sample question to run immediately:</span>
        <div class="prompts-grid">
          <button
            v-for="(p, pIdx) in samplePrompts"
            :key="pIdx"
            class="empty-prompt-btn"
            @click="runSamplePrompt(p)"
          >
            <Icon name="sparkles" :size="12" />
            <span>{{ p }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import Icon from '@/components/common/Icon.vue'

const chatStore = useChatStore()
const authStore = useAuthStore()

const currencySymbol = ref(import.meta.env.VITE_CURRENCY_SYMBOL || '₹')
const activeQuery = computed(() => chatStore.activeQueryResult)

const tableSearchQuery = ref('')
const sortColumn = ref('')
const sortAsc = ref(true)
const isCopied = ref(false)

const samplePrompts = [
  'Top 5 subscriptions by monthly spend',
  'Which subscriptions renew in next 30 days?',
  'Show total monthly spend by category',
  'Find all dormant license seats',
  'Show pending or overdue invoices',
]

function runSamplePrompt(prompt) {
  chatStore.sendMessage(prompt, authStore.user.role, authStore.user.email)
}

function sortByColumn(col) {
  if (sortColumn.value === col) {
    sortAsc.value = !sortAsc.value
  } else {
    sortColumn.value = col
    sortAsc.value = true
  }
}

function isNumeric(val) {
  if (val === null || val === undefined || val === '') return false
  return !isNaN(Number(val))
}

function isCurrencyColumn(col) {
  const c = col.toLowerCase()
  return c.includes('cost') || c.includes('amount') || c.includes('spend') || c.includes('acv') || c.includes('price') || c.includes('budget') || c.includes('savings')
}

function isStatusColumn(col) {
  return col.toLowerCase() === 'status' || col.toLowerCase().includes('payment_status')
}

const filteredAndSortedRows = computed(() => {
  if (!activeQuery.value || !activeQuery.value.rows) return []
  let rows = [...activeQuery.value.rows]

  // Filter
  if (tableSearchQuery.value.trim()) {
    const q = tableSearchQuery.value.toLowerCase().trim()
    rows = rows.filter(r => {
      return Object.values(r).some(val => String(val || '').toLowerCase().includes(q))
    })
  }

  // Sort
  if (sortColumn.value) {
    const col = sortColumn.value
    rows.sort((a, b) => {
      const valA = a[col]
      const valB = b[col]
      if (valA === valB) return 0
      if (valA === null || valA === undefined) return 1
      if (valB === null || valB === undefined) return -1
      if (isNumeric(valA) && isNumeric(valB)) {
        return sortAsc.value ? Number(valA) - Number(valB) : Number(valB) - Number(valA)
      }
      return sortAsc.value
        ? String(valA).localeCompare(String(valB))
        : String(valB).localeCompare(String(valA))
    })
  }

  return rows
})

// --- Table Pagination Logic ---
const currentPage = ref(1)
const pageSize = ref(40)

// Reset page to 1 when search query or active query changes
watch([tableSearchQuery, () => activeQuery.value?.id], () => {
  currentPage.value = 1
})

const totalPages = computed(() => {
  if (pageSize.value === -1) return 1
  return Math.ceil(filteredAndSortedRows.value.length / pageSize.value) || 1
})

const paginatedRows = computed(() => {
  if (pageSize.value === -1 || filteredAndSortedRows.value.length <= pageSize.value) {
    return filteredAndSortedRows.value
  }
  const start = (currentPage.value - 1) * pageSize.value
  return filteredAndSortedRows.value.slice(start, start + pageSize.value)
})

const pageStartRecord = computed(() => {
  if (filteredAndSortedRows.value.length === 0) return 0
  if (pageSize.value === -1) return 1
  return (currentPage.value - 1) * pageSize.value + 1
})

const pageEndRecord = computed(() => {
  if (pageSize.value === -1) return filteredAndSortedRows.value.length
  return Math.min(currentPage.value * pageSize.value, filteredAndSortedRows.value.length)
})

function goToPage(p) {
  if (p < 1) p = 1
  if (p > totalPages.value) p = totalPages.value
  currentPage.value = p
}

const visiblePages = computed(() => {
  const pages = []
  const maxButtons = 5
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + maxButtons - 1)
  if (end - start < maxButtons - 1) {
    start = Math.max(1, end - maxButtons + 1)
  }
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

function isIdentifierColumn(col) {
  if (!col) return false
  const c = col.toLowerCase().trim()
  return c === 'id' || c.endsWith('_id') || c.startsWith('id_') || c.endsWith('_code') || c === 'pk' || c === 'fk'
}

const datasetLabel = computed(() => {
  if (!activeQuery.value || !activeQuery.value.rows) return 'Records returned'
  const cols = (activeQuery.value.columns || []).map(c => c.toLowerCase())
  if (cols.includes('product_name') || cols.includes('monthly_cost')) return 'SaaS Subscriptions'
  if (cols.includes('email') || cols.includes('full_name') || cols.includes('role')) return 'Workspace Users'
  if (cols.includes('invoice_number') || cols.includes('payment_status')) return 'Billing Invoices'
  if (cols.includes('seat_type') || cols.includes('last_activity_date')) return 'License Allocations'
  if (cols.includes('department_name') || cols.includes('budget_annual')) return 'Departments'
  return 'Matching Records'
})

const computedTotalValue = computed(() => {
  if (!activeQuery.value || !activeQuery.value.rows || !activeQuery.value.rows.length) return 0
  const cols = activeQuery.value.columns || []
  const costCol = cols.find(c => isCurrencyColumn(c) && !isIdentifierColumn(c))
  if (!costCol) return 0
  return activeQuery.value.rows.reduce((sum, r) => sum + (Number(r[costCol]) || 0), 0)
})

const averageSpendValue = computed(() => {
  if (!computedTotalValue.value || !activeQuery.value?.rows?.length) return 0
  return Math.round(computedTotalValue.value / activeQuery.value.rows.length)
})

// Highest Expense Item
const highestCostItem = computed(() => {
  if (!activeQuery.value || !activeQuery.value.rows || !activeQuery.value.rows.length) return null
  const cols = activeQuery.value.columns || []
  const costCol = cols.find(c => isCurrencyColumn(c) && !isIdentifierColumn(c))
  if (!costCol) return null

  const nameCol = cols.find(c => ['product_name', 'name', 'full_name', 'department', 'vendor', 'category'].includes(c.toLowerCase())) || cols[0]

  let maxRow = activeQuery.value.rows[0]
  let maxVal = Number(maxRow[costCol]) || 0

  for (const r of activeQuery.value.rows) {
    const val = Number(r[costCol]) || 0
    if (val > maxVal) {
      maxVal = val
      maxRow = r
    }
  }

  if (maxVal <= 0) return null
  return {
    name: String(maxRow[nameCol] || 'Service'),
    val: maxVal
  }
})

// Lowest Expense Item
const lowestCostItem = computed(() => {
  if (!activeQuery.value || !activeQuery.value.rows || activeQuery.value.rows.length < 2) return null
  const cols = activeQuery.value.columns || []
  const costCol = cols.find(c => isCurrencyColumn(c) && !isIdentifierColumn(c))
  if (!costCol) return null

  const nameCol = cols.find(c => ['product_name', 'name', 'full_name', 'department', 'vendor', 'category'].includes(c.toLowerCase())) || cols[0]

  let minRow = activeQuery.value.rows[0]
  let minVal = Number(minRow[costCol]) || Infinity

  for (const r of activeQuery.value.rows) {
    const val = Number(r[costCol]) || 0
    if (val > 0 && val < minVal) {
      minVal = val
      minRow = r
    }
  }

  if (minVal === Infinity || minVal <= 0) return null
  return {
    name: String(minRow[nameCol] || 'Service'),
    val: minVal
  }
})

// Fallback non-ID top contributor
const topNonIdContributor = computed(() => {
  if (highestCostItem.value) return null
  if (!effectiveChart.value || !effectiveChart.value.labels) return null
  const vals = effectiveChart.value.values || []
  const labels = effectiveChart.value.labels || []
  if (!vals.length || !labels.length) return null
  const maxVal = Math.max(...vals)
  const maxIdx = vals.indexOf(maxVal)
  return {
    label: 'Leading Metric',
    name: labels[maxIdx],
    val: maxVal
  }
})

// Deep Subscription Audit Summary
const auditSummary = computed(() => {
  if (!activeQuery.value || !activeQuery.value.rows || activeQuery.value.rows.length !== 1) return null
  const r = activeQuery.value.rows[0]
  if (!('total_seats_licensed' in r) || !('assigned_users_count' in r || 'cost_per_user' in r || 'unallocated_seats' in r || 'dormant_seats' in r)) return null
  const totalSeats = Number(r.total_seats_licensed || 0)
  const assignedUsers = Number(r.assigned_users_count || 0)
  const unallocatedSeats = r.unallocated_seats !== undefined ? Number(r.unallocated_seats) : Math.max(0, totalSeats - assignedUsers)
  const dormantSeats = Number(r.dormant_seats || 0)
  const activeInUseSeats = Math.max(0, assignedUsers - dormantSeats)
  const monthlyCost = Number(r.monthly_cost || 0)
  const costPerSeat = totalSeats > 0 ? (monthlyCost / totalSeats) : 0
  const costPerUser = Number(r.cost_per_user || (assignedUsers > 0 ? (monthlyCost / assignedUsers).toFixed(2) : costPerSeat.toFixed(2)))
  const unallocatedWaste = Number(r.unallocated_waste || (unallocatedSeats * costPerSeat).toFixed(2))
  const dormantWaste = Number(r.dormant_waste || (dormantSeats * costPerSeat).toFixed(2))
  const totalWaste = Math.round(unallocatedWaste + dormantWaste)
  const optimizationPct = monthlyCost > 0 ? Math.round(((unallocatedWaste + dormantWaste) / monthlyCost) * 100) : 0
  return {
    productName: r.product_name || 'Subscription',
    monthlyCost,
    totalSeats,
    assignedUsers,
    activeInUseSeats,
    dormantSeats,
    unallocatedSeats,
    costPerUser,
    costPerSeat,
    unallocatedWaste,
    dormantWaste,
    totalWaste,
    optimizationPct,
    allocationRate: totalSeats > 0 ? Math.round((assignedUsers / totalSeats) * 100) : 0
  }
})

// Cost Optimization & Recommendation Impact Summary
const recommendationSummary = computed(() => {
  if (!activeQuery.value || !activeQuery.value.rows || activeQuery.value.rows.length !== 1) return null
  const r = activeQuery.value.rows[0]
  if (!('estimated_monthly_savings' in r || 'estimated_annual_savings' in r)) return null

  const productName = r.product_name || 'Subscription'
  const monthlySavings = Number(r.estimated_monthly_savings || 0)
  const annualSavings = Number(r.estimated_annual_savings || (monthlySavings * 12))

  let monthlyCost = Number(r.monthly_cost || 0)
  let annualCost = Number(r.annual_contract_value || (monthlyCost * 12))

  // If cost was provided via chart values [annualCost, annualSavings]
  if (annualCost === 0 && activeQuery.value.chart?.values?.length >= 2) {
    annualCost = Number(activeQuery.value.chart.values[0] || 0)
    monthlyCost = Math.round(annualCost / 12)
  }

  const recType = r.recommendation_type ? String(r.recommendation_type).replace(/_/g, ' ').toUpperCase() : 'OPTIMIZATION'
  const confidenceScore = r.confidence_score ? Math.round(Number(r.confidence_score) * 100) : 95
  const description = r.description || ''
  const status = r.status || 'detected'

  return {
    productName,
    monthlySavings,
    annualSavings,
    monthlyCost,
    annualCost,
    recType,
    confidenceScore,
    description,
    status
  }
})

const effectiveChart = computed(() => {
  // 1. If this is an audit query and we have audit metrics
  if (auditSummary.value) {
    const s = auditSummary.value
    if (activeQuery.value?.chart?.labels && activeQuery.value.chart.labels.length > 1) {
      return activeQuery.value.chart
    }
    return {
      type: 'doughnut',
      title: `Seat Allocation & Optimization Breakdown (${s.productName})`,
      labels: ['Active In-Use Seats', 'Dormant Inactive Seats', 'Unallocated Idle Seats'],
      values: [s.activeInUseSeats, s.dormantSeats, s.unallocatedSeats],
      value_column: 'seats'
    }
  }

  // 2. If this is a cost recommendation query and we have recommendation metrics
  if (recommendationSummary.value) {
    const rec = recommendationSummary.value
    if (activeQuery.value?.chart?.labels && activeQuery.value.chart.labels.length > 1) {
      return activeQuery.value.chart
    }
    return {
      type: 'doughnut',
      title: `Annual Cost Impact & Optimization Savings (${rec.productName})`,
      labels: ['Current Annual Contract', 'Projected Annual Savings'],
      values: [rec.annualCost, rec.annualSavings],
      value_column: 'amount'
    }
  }

  // 3. If backend returned a valid chart that DOES NOT plot database IDs
  if (activeQuery.value?.chart?.labels?.length) {
    const valCol = String(activeQuery.value.chart.value_column || '').toLowerCase()
    const title = String(activeQuery.value.chart.title || '').toLowerCase()
    if (!isIdentifierColumn(valCol) && !title.includes('id by')) {
      if (activeQuery.value.chart.labels.length > 1 || activeQuery.value.rows?.length > 1) {
        return activeQuery.value.chart
      }
    }
  }

  if (!activeQuery.value?.rows?.length || !activeQuery.value?.columns?.length || activeQuery.value.rows.length <= 1) {
    return null
  }
  const rows = activeQuery.value.rows
  const cols = activeQuery.value.columns

  // Find a string label column (excluding IDs and dates)
  const labelCandidates = ['product_name', 'category', 'department', 'vendor', 'name', 'full_name', 'role', 'status']
  let labelCol = cols.find(c => labelCandidates.includes(c.toLowerCase()))

  if (!labelCol) {
    labelCol = cols.find(c => {
      if (isIdentifierColumn(c) || c.includes('date')) return false
      const val = rows[0]?.[c]
      return typeof val === 'string' && isNaN(Number(val))
    }) || cols[0]
  }

  // Find a numeric column (Prioritize Currency first, then non-ID numerics)
  const numCol = cols.find(c => isCurrencyColumn(c) && !isIdentifierColumn(c) && isNumeric(rows[0]?.[c]))
    || cols.find(c => !isIdentifierColumn(c) && !c.includes('date') && isNumeric(rows[0]?.[c]))

  if (!labelCol || !numCol || labelCol === numCol || isIdentifierColumn(numCol)) {
    return null
  }

  // Slice top 8 entries sorted descending by value for a clear, readable chart
  const sorted = [...rows].sort((a, b) => (Number(b[numCol]) || 0) - (Number(a[numCol]) || 0))
  const slice = sorted.slice(0, 8)
  const labels = slice.map(r => String(r[labelCol] || '').substring(0, 28))
  const values = slice.map(r => Number(r[numCol]) || 0)

  return {
    type: labels.length <= 6 ? 'doughnut' : 'bar',
    title: `${formatColumnHeader(numCol)} Breakdown`,
    value_column: numCol,
    label_column: labelCol,
    labels,
    values,
  }
})

const donutSegments = computed(() => {
  if (!effectiveChart.value || !effectiveChart.value.values || !effectiveChart.value.values.length) return []
  const values = effectiveChart.value.values.map(v => Math.max(0, Number(v) || 0))
  const total = values.reduce((sum, v) => sum + v, 0)
  if (total <= 0) return []

  const radius = 50
  const circumference = 2 * Math.PI * radius // ~314.159
  let accumulatedFraction = 0

  return values.map((val, idx) => {
    const fraction = val / total
    const strokeDasharray = `${(fraction * circumference).toFixed(2)} ${circumference.toFixed(2)}`
    const strokeDashoffset = `${(-accumulatedFraction * circumference).toFixed(2)}`
    accumulatedFraction += fraction
    const pct = Math.round(fraction * 100)
    return {
      label: effectiveChart.value.labels[idx] || `Item ${idx + 1}`,
      value: val,
      pct,
      color: getBarColor(idx),
      strokeDasharray,
      strokeDashoffset,
    }
  })
})

const isDoughnutOrPie = computed(() => {
  if (!effectiveChart.value) return false
  return effectiveChart.value.type === 'doughnut' || effectiveChart.value.type === 'pie' || Boolean(recommendationSummary.value) || Boolean(auditSummary.value) || (effectiveChart.value.labels && effectiveChart.value.labels.length <= 6)
})

const donutCenterLabel = computed(() => {
  if (recommendationSummary.value) return 'ANNUAL SAVINGS'
  if (auditSummary.value) return 'RECOVERABLE'
  return 'TOTAL SHARE'
})

const donutCenterValue = computed(() => {
  if (recommendationSummary.value) {
    const s = recommendationSummary.value
    return `+${currencySymbol.value}${formatCompactNumber(s.annualSavings)}`
  }
  if (auditSummary.value) {
    return `${auditSummary.value.optimizationPct}%`
  }
  return `${donutSegments.value.length} Metrics`
})

function formatCompactNumber(num) {
  if (!num) return '0'
  const n = Number(num)
  if (n >= 10000000) return (n / 10000000).toFixed(1) + 'Cr'
  if (n >= 100000) return (n / 100000).toFixed(1) + 'L'
  if (n >= 1000) return (n / 1000).toFixed(0) + 'k'
  return n.toLocaleString('en-IN')
}

function calculatePercentage(val, allVals) {
  const max = Math.max(...allVals, 1)
  return Math.max(10, Math.round((Number(val || 0) / max) * 100))
}

function getBarColor(idx) {
  const colors = ['#0ea5e9', '#10b981', '#f59e0b', '#ec4899', '#38bdf8', '#8b5cf6']
  return colors[idx % colors.length]
}

function formatColumnHeader(col) {
  return col.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function getStatusClass(val) {
  const v = String(val).toLowerCase()
  if (v === 'active' || v === 'paid') return 'status-active'
  if (v === 'pending' || v === 'trial') return 'status-pending'
  if (v === 'overdue' || v === 'cancelled') return 'status-danger'
  return ''
}

function getCellAlignment(col, val) {
  if (isNumeric(val) && !isStatusColumn(col)) return 'text-right'
  return ''
}

function formatCellValue(val) {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'boolean') return val ? 'Yes' : 'No'
  if (typeof val === 'number') return val.toLocaleString('en-IN')
  return String(val)
}

function formatNumber(val) {
  const num = Number(val)
  return isNaN(num) ? val : num.toLocaleString('en-IN')
}

function formatChartVal(val) {
  const chart = effectiveChart.value
  const isCurrency = chart && (
    (chart.value_column && isCurrencyColumn(chart.value_column)) ||
    (chart.title && (chart.title.toLowerCase().includes('spend') || chart.title.toLowerCase().includes('cost') || chart.title.toLowerCase().includes('acv') || chart.title.toLowerCase().includes('amount') || chart.title.toLowerCase().includes('savings') || chart.title.toLowerCase().includes('budget')))
  )
  const n = Number(val)
  const formatted = isNaN(n) ? val : n.toLocaleString('en-IN')
  return isCurrency ? `${currencySymbol.value}${formatted}` : formatted
}

function formatModelName(modelId) {
  if (!modelId) return ''
  return modelId.replace('openai/', '').replace('google/', '').replace(/-/g, ' ').toUpperCase()
}

function formatInsightText(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

function exportCSV() {
  if (!activeQuery.value || !activeQuery.value.rows || !activeQuery.value.rows.length) return
  const cols = activeQuery.value.columns
  const rows = activeQuery.value.rows

  const header = cols.join(',')
  const csvRows = rows.map(r => cols.map(c => `"${String(r[c] ?? '').replace(/"/g, '""')}"`).join(','))
  const csvContent = [header, ...csvRows].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `subscriptiq_analysis_${Date.now()}.csv`)
  link.click()
  URL.revokeObjectURL(url)
}

function exportJSON() {
  if (!activeQuery.value || !activeQuery.value.rows) return
  const dataStr = JSON.stringify(activeQuery.value.rows, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `subscriptiq_analysis_${Date.now()}.json`)
  link.click()
  URL.revokeObjectURL(url)
}

function copyTableData() {
  if (!activeQuery.value || !activeQuery.value.rows) return
  const cols = activeQuery.value.columns
  const rows = activeQuery.value.rows
  const tsv = [
    cols.join('\t'),
    ...rows.map(r => cols.map(c => String(r[c] ?? '')).join('\t'))
  ].join('\n')

  navigator.clipboard.writeText(tsv)
  isCopied.value = true
  setTimeout(() => {
    isCopied.value = false
  }, 2000)
}
</script>

<style scoped>
.query-analysis-view {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Loading Card */
.analysis-loading-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 40px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
}

.loading-spinner-wrap {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quantum-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(56, 189, 248, 0.2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-label {
  font-size: 10.5px;
  letter-spacing: 0.08em;
  color: var(--accent);
}

.loading-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 4px;
}

.loading-subtitle {
  font-size: 11.5px;
  color: var(--text-muted);
  margin-top: 4px;
}

.analysis-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Header Card */
.analysis-header-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.header-top-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.query-title-group {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.query-icon-pill {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--accent-light);
  border: 1px solid rgba(56, 189, 248, 0.3);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.query-icon-pill.is-blocked {
  background: var(--danger-bg);
  border-color: rgba(239, 68, 68, 0.3);
  color: var(--danger);
}

.query-meta-tag {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--accent);
  margin-bottom: 2px;
}

.query-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
}

.header-action-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--accent);
}

/* Telemetry Strip */
.telemetry-badges-strip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--border-subtle);
  font-size: 11px;
  flex-wrap: wrap;
}

.telemetry-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.telemetry-label {
  color: var(--text-muted);
}

.telemetry-val {
  color: var(--text-primary);
}

.telemetry-val.highlight {
  color: var(--accent);
  font-weight: 600;
}

.telemetry-divider {
  width: 1px;
  height: 12px;
  background-color: var(--border-color);
}

.status-badge {
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

.badge-success {
  background-color: var(--success-bg);
  color: var(--success);
}

.badge-blocked {
  background-color: var(--danger-bg);
  color: var(--danger);
}

.type-pill {
  padding: 1px 6px;
  border-radius: 4px;
  background-color: var(--bg-tertiary);
  color: var(--accent);
  font-size: 10px;
}

/* Guardrail Alert Card */
.guardrail-alert-card {
  background: var(--danger-bg);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-md);
  padding: 14px 18px;
  display: flex;
  gap: 14px;
}

.alert-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.2);
  color: var(--danger);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-text-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.alert-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--danger);
}

.alert-body {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.45;
}

.alert-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* Insight Summary Card */
.insight-summary-card {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.07) 0%, rgba(2, 132, 199, 0.03) 100%);
  border: 1px solid rgba(56, 189, 248, 0.22);
  border-radius: var(--radius-md);
  padding: 14px 18px;
  display: flex;
  gap: 14px;
}

.insight-beacon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--accent-gradient);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.insight-text-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.insight-heading {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent);
}

.insight-body {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.5;
}

.insight-explanation {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* Visual Analytics Grid */
.visual-analytics-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

@media (max-width: 900px) {
  .visual-analytics-grid {
    grid-template-columns: 1fr;
  }
}

.chart-main-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chart-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-metric-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  background-color: var(--bg-tertiary);
  color: var(--text-muted);
}

.chart-header-badges {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-type-pill {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.25);
  letter-spacing: 0.05em;
}

.chart-layout-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-layout-body.with-donut {
  display: grid;
  grid-template-columns: 175px 1fr;
  align-items: center;
  gap: 20px;
}

@media (max-width: 768px) {
  .chart-layout-body.with-donut {
    grid-template-columns: 1fr;
    justify-items: center;
  }
}

.donut-chart-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  padding: 4px;
}

.donut-svg-container {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
  overflow: visible;
}

.donut-bg-ring {
  stroke: var(--bg-tertiary);
  opacity: 0.6;
}

.donut-segment {
  stroke-linecap: round;
  transition: stroke-dasharray 0.6s cubic-bezier(0.16, 1, 0.3, 1), stroke-dashoffset 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.12));
}

.donut-segment:hover {
  stroke-width: 18;
  opacity: 0.95;
  cursor: pointer;
}

.donut-center-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  text-align: center;
  width: 76px;
}

.donut-center-tag {
  font-size: 8px;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  font-weight: 600;
  line-height: 1;
  text-transform: uppercase;
}

.donut-center-main {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  margin: 2px 0 1px;
}

.donut-center-sub {
  font-size: 8px;
  color: #10b981;
  font-weight: 600;
  letter-spacing: 0.05em;
  line-height: 1;
}

.chart-bars-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.chart-bar-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bar-info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
}

.bar-label-with-dot {
  display: flex;
  align-items: center;
  gap: 7px;
  max-width: 250px;
}

.legend-color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.bar-item-label {
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bar-value-with-pct {
  display: flex;
  align-items: center;
  gap: 6px;
}

.bar-item-value {
  color: var(--text-primary);
  font-weight: 600;
}

.bar-item-pct {
  font-size: 10px;
  color: var(--text-muted);
  font-weight: 500;
}

.bar-track-wrap {
  width: 100%;
  height: 8px;
  background-color: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill-dynamic {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.kpi-side-column {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-kpi-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kpi-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kpi-number {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.kpi-number.text-accent {
  color: var(--accent);
}

.kpi-number.text-highlight {
  color: #10b981;
  font-size: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kpi-number.text-muted-bright {
  color: #38bdf8;
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kpi-subtext {
  font-size: 10.5px;
  color: var(--text-muted);
}

.subtext-pct {
  font-weight: 500;
  opacity: 0.85;
  margin-left: 3px;
}

.rec-highlight-card {
  border-color: rgba(16, 185, 129, 0.35);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.03) 100%);
}

.text-strategy {
  font-size: 13.5px;
  font-weight: 700;
  color: #38bdf8;
  letter-spacing: 0.02em;
}

.text-success {
  color: #10b981;
  display: flex;
  align-items: center;
  gap: 6px;
}

.conf-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
  display: inline-block;
}

/* Full Table Card */
.full-table-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.table-toolbar {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.table-toolbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.table-rows-counter {
  font-size: 11px;
  color: var(--text-muted);
}

.search-filter-box {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
}

.search-icon {
  color: var(--text-muted);
}

.search-input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 11.5px;
  outline: none;
  width: 150px;
}

.clear-search-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
}

/* Data Table */
.table-responsive-scroll {
  max-height: 480px;
  overflow: auto;
}

.in-depth-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11.5px;
}

.in-depth-data-table th,
.in-depth-data-table td {
  padding: 9px 14px;
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
  white-space: nowrap;
}

.in-depth-data-table th {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 5;
  user-select: none;
}

.sortable-th {
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.sortable-th:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.th-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.sort-indicator {
  font-size: 9px;
  color: var(--text-muted);
}

.sortable-th.is-sorted .sort-indicator {
  color: var(--accent);
}

.in-depth-data-table tbody tr:hover {
  background-color: var(--bg-hover);
}

.text-right {
  text-align: right;
}

/* Status Chips */
.status-chip {
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  display: inline-block;
  text-transform: capitalize;
}

.status-active {
  background-color: var(--success-bg);
  color: var(--success);
}

.status-pending {
  background-color: var(--warning-bg);
  color: var(--warning);
}

.status-danger {
  background-color: var(--danger-bg);
  color: var(--danger);
}

.empty-search-cell {
  text-align: center;
  padding: 28px;
  color: var(--text-muted);
  font-style: italic;
}

/* Zero Rows Card */
.zero-rows-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 32px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 10px;
}

.zero-rows-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background-color: var(--bg-tertiary);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
}

.zero-rows-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.zero-rows-desc {
  font-size: 12.5px;
  color: var(--text-muted);
  max-width: 420px;
}

/* Empty State Card */
.empty-state-card {
  background-color: var(--bg-card);
  border: 1px dashed var(--border-color);
  border-radius: var(--radius-lg);
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 14px;
  max-width: 640px;
  margin: 40px auto;
}

.empty-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: var(--accent-light);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.empty-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  max-width: 480px;
}

.empty-quick-prompts {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
  width: 100%;
}

.empty-prompts-label {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 500;
}

.prompts-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.empty-prompt-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: var(--radius-full);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.empty-prompt-btn:hover {
  background-color: var(--bg-active);
  color: var(--accent);
  border-color: var(--accent);
  transform: translateY(-1px);
}

/* S.No Column */
.sno-th {
  width: 48px;
  text-align: center !important;
  color: var(--text-muted);
}

.sno-cell {
  text-align: center;
  color: var(--text-muted);
  font-weight: 500;
  width: 48px;
}

/* Table Pagination Bar */
.table-pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  font-size: 11.5px;
  flex-wrap: wrap;
  gap: 12px;
}

.pagination-info {
  color: var(--text-secondary);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pagination-btn {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: 11.5px;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--accent);
  color: var(--accent);
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-page-pills {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-page-pill {
  min-width: 28px;
  height: 26px;
  padding: 0 6px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 11.5px;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-page-pill:hover:not(.active) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.pagination-page-pill.active {
  background: var(--accent);
  color: #ffffff;
  border-color: var(--accent);
  font-weight: 600;
}

.pagination-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
}

.size-select {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  outline: none;
  cursor: pointer;
}

.audit-waste-card {
  border-color: rgba(245, 158, 11, 0.35);
  background: rgba(245, 158, 11, 0.05);
}

.text-warning {
  color: #f59e0b !important;
}

.subtext-unit {
  font-size: 13px;
  font-weight: 500;
  margin-left: 2px;
}
</style>
