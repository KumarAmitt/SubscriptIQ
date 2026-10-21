<template>
  <div class="about-view-container font-sans">
    <!-- Hero Section: Clear Enterprise Value -->
    <header class="about-hero-section">
      <div class="hero-badge">
        <Icon name="sparkles" :size="13" class="hero-badge-icon" />
        <span>ENTERPRISE SAAS &amp; LICENSE MANAGEMENT</span>
      </div>

      <h1 class="hero-title">
        Take Total Control of Your <span class="hero-title-highlight">Enterprise SaaS Subscriptions</span>, Licenses &amp; Spend
      </h1>

      <p class="hero-subtitle">
        SubscriptIQ eliminates subscription chaos, runaway software expenses, and renewal surprises. Say goodbye to outdated spreadsheets and endless IT tickets—simply chat with your AI Copilot to get instant, audit-ready visibility into every software tool, license seat, and dollar spent across your enterprise.
      </p>

      <!-- Key Value Metrics Bar -->
      <div class="hero-stats-grid">
        <div class="hero-stat-card">
          <div class="stat-icon-wrap text-warning">
            <Icon name="target" :size="18" />
          </div>
          <div class="stat-number font-mono">30%+</div>
          <div class="stat-label">Average Cost Reduction</div>
          <div class="stat-sub">Identified by reclaiming dormant and unallocated seats</div>
        </div>

        <div class="hero-stat-card">
          <div class="stat-icon-wrap text-accent">
            <Icon name="dashboard" :size="18" />
          </div>
          <div class="stat-number font-mono">Zero</div>
          <div class="stat-label">Spreadsheet Chaos</div>
          <div class="stat-sub">One unified, real-time command center for all tools &amp; contracts</div>
        </div>

        <div class="hero-stat-card">
          <div class="stat-icon-wrap text-success">
            <Icon name="zap" :size="18" />
          </div>
          <div class="stat-number font-mono">100%</div>
          <div class="stat-label">Renewal Visibility</div>
          <div class="stat-sub">Proactive 30/60/90-day alerts to negotiate before auto-renews</div>
        </div>

        <div class="hero-stat-card">
          <div class="stat-icon-wrap text-info">
            <Icon name="sparkles" :size="18" />
          </div>
          <div class="stat-number font-mono">Instant</div>
          <div class="stat-label">Conversational Answers</div>
          <div class="stat-sub">Ask naturally in plain English—no technical skills or SQL needed</div>
        </div>
      </div>

      <div class="hero-cta-actions">
        <button class="primary-cta-btn" @click="uiStore.setActiveNav('dashboard')">
          <Icon name="dashboard" :size="15" />
          <span>Open Subscription Dashboard</span>
        </button>
        <button class="secondary-cta-btn" @click="uiStore.toggleChat">
          <Icon name="sparkles" :size="15" />
          <span>Ask Your AI Assistant</span>
        </button>
      </div>
    </header>

    <!-- Section 1: The Problem & The Transformation (Before vs. After) -->
    <section class="content-section">
      <div class="section-header-block">
        <span class="section-tag font-mono">THE SAAS DILEMMA</span>
        <h2 class="section-heading">Managing Enterprise Software Used to Be a Nightmare</h2>
        <p class="section-lead">
          As companies adopt dozens of cloud applications, subscription management breaks down across fragmented departments, causing massive financial waste and operational headaches.
        </p>
      </div>

      <div class="comparison-grid">
        <!-- Without SubscriptIQ -->
        <div class="comparison-card without-card">
          <div class="card-badge without-badge">
            <span>WITHOUT SUBSCRIPTIQ</span>
          </div>
          <h3 class="comparison-title">The Pain of Traditional Management</h3>
          <ul class="pain-points-list">
            <li>
              <div class="bullet-cross">✕</div>
              <div>
                <strong>Hidden License Waste:</strong> Inactive employees and departed staff quietly consume expensive $150+/mo seats for months without anyone noticing.
              </div>
            </li>
            <li>
              <div class="bullet-cross">✕</div>
              <div>
                <strong>Surprise Auto-Renewals:</strong> Contracts renew automatically with 5-10% price hikes because notice windows slipped past unnoticed.
              </div>
            </li>
            <li>
              <div class="bullet-cross">✕</div>
              <div>
                <strong>Spreadsheet Blindspots:</strong> Finance and IT maintain separate, out-of-date spreadsheets that fail to reflect actual tool usage.
              </div>
            </li>
            <li>
              <div class="bullet-cross">✕</div>
              <div>
                <strong>Slow Answers &amp; IT Tickets:</strong> Getting answers about departmental spend or who owns what license takes days of back-and-forth tickets.
              </div>
            </li>
          </ul>
        </div>

        <!-- With SubscriptIQ -->
        <div class="comparison-card with-card">
          <div class="card-badge with-badge">
            <Icon name="sparkles" :size="12" />
            <span>WITH SUBSCRIPTIQ</span>
          </div>
          <h3 class="comparison-title">The Effortless Modern Experience</h3>
          <ul class="benefits-points-list">
            <li>
              <div class="bullet-check">✓</div>
              <div>
                <strong>Automated Waste Reclamation:</strong> Instantly detects dormant seats (&gt;30 days inactive) and unallocated licenses, showing exact dollar savings.
              </div>
            </li>
            <li>
              <div class="bullet-check">✓</div>
              <div>
                <strong>Proactive Renewal Radar:</strong> 30/60/90-day visual renewal horizon gives your team total leverage to downsize or renegotiate terms.
              </div>
            </li>
            <li>
              <div class="bullet-check">✓</div>
              <div>
                <strong>Single Source of Truth:</strong> Real-time synchronization across subscriptions, active licenses, invoices, and employee assignments.
              </div>
            </li>
            <li>
              <div class="bullet-check">✓</div>
              <div>
                <strong>Instant Answers in Plain English:</strong> Ask "What tools does Alex have?" or "Show top spend by category" and receive verified data in seconds.
              </div>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Section 2: How It Makes Your Life Easy (Core Features) -->
    <section class="content-section">
      <div class="section-header-block">
        <span class="section-tag font-mono">ENTERPRISE CAPABILITIES</span>
        <h2 class="section-heading">How SubscriptIQ Makes Everyday Subscription Management Effortless</h2>
        <p class="section-lead">
          Everything you need to eliminate waste, streamline employee provisioning, and maintain total mastery over corporate contracts.
        </p>
      </div>

      <div class="features-mosaic-grid">
        <div class="feature-card" v-for="(feat, idx) in enterpriseFeatures" :key="idx">
          <div class="feature-icon-header">
            <div class="feature-icon-beacon" :style="{ backgroundColor: feat.bg, color: feat.color }">
              <Icon :name="feat.icon" :size="18" />
            </div>
            <span class="feature-badge font-mono">{{ feat.category }}</span>
          </div>
          <h3 class="feature-title">{{ feat.title }}</h3>
          <p class="feature-description">{{ feat.description }}</p>

          <div class="feature-highlight-box">
            <span class="highlight-label font-mono">SAMPLE PROMPT TO TRY:</span>
            <button class="sample-query-pill" @click="tryQuery(feat.sampleQuery)">
              <span>"{{ feat.sampleQuery }}"</span>
              <Icon name="arrow-right" :size="12" />
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 3: Value for Various Roles (How It Makes Life Easy) -->
    <section class="content-section bg-gradient-panel">
      <div class="section-header-block">
        <span class="section-tag font-mono">DESIGNED FOR YOUR TEAM</span>
        <h2 class="section-heading">Tailored Benefits for Every Department in Your Organization</h2>
        <p class="section-lead">
          Whether you manage budgets, provision tools, negotiate vendor contracts, or lead a division, SubscriptIQ solves your biggest subscription headaches.
        </p>
      </div>

      <!-- Role Selector Tabs -->
      <div class="role-tabs-bar">
        <button
          v-for="role in userRoles"
          :key="role.id"
          class="role-tab-btn"
          :class="{ 'is-active': activeRoleId === role.id }"
          @click="activeRoleId = role.id"
        >
          <span class="role-emoji">{{ role.emoji }}</span>
          <span>{{ role.title }}</span>
        </button>
      </div>

      <!-- Active Role Details Card -->
      <div class="role-detail-card" v-if="selectedRole">
        <div class="role-card-header">
          <div class="role-avatar-wrap">
            <span class="role-large-emoji">{{ selectedRole.emoji }}</span>
          </div>
          <div class="role-title-column">
            <h3 class="role-headline">{{ selectedRole.headline }}</h3>
            <span class="role-mission-statement">{{ selectedRole.mission }}</span>
          </div>
        </div>

        <div class="role-benefits-grid">
          <div class="benefit-item" v-for="(b, bIdx) in selectedRole.benefits" :key="bIdx">
            <div class="benefit-check">
              <Icon name="check-circle" :size="16" />
            </div>
            <div class="benefit-text">
              <h4 class="benefit-name">{{ b.title }}</h4>
              <p class="benefit-explanation">{{ b.desc }}</p>
            </div>
          </div>
        </div>

        <div class="role-action-footer">
          <span class="footer-note font-mono">HOW TO USE IT IN YOUR DAILY WORKFLOW:</span>
          <p class="workflow-text">{{ selectedRole.workflow }}</p>
        </div>
      </div>
    </section>

    <!-- Section 4: Enterprise Safety & Trust (How It Works Under the Hood) -->
    <section class="content-section">
      <div class="section-header-block">
        <span class="section-tag font-mono">ENTERPRISE-GRADE TRUST</span>
        <h2 class="section-heading">Complete Read-Only Safety &amp; Verified Accuracy</h2>
        <p class="section-lead">
          SubscriptIQ is designed from the ground up for strict corporate environments where data integrity and security are non-negotiable.
        </p>
      </div>

      <div class="trust-grid">
        <div class="trust-card">
          <div class="trust-icon text-success">
            <Icon name="lock" :size="20" />
          </div>
          <h3 class="trust-title">100% Read-Only Safety</h3>
          <p class="trust-desc">
            Your database is completely shielded. Multi-stage security guardrails automatically block any modifying commands (DROP, DELETE, UPDATE, INSERT), ensuring your data remains pristine.
          </p>
        </div>

        <div class="trust-card">
          <div class="trust-icon text-accent">
            <Icon name="target" :size="20" />
          </div>
          <h3 class="trust-title">Zero Guesswork Accuracy</h3>
          <p class="trust-desc">
            Unlike generic AI chat tools that hallucinate numbers, SubscriptIQ uses verified schema linking and AST parsing to query your actual PostgreSQL database with mathematical precision.
          </p>
        </div>

        <div class="trust-card">
          <div class="trust-icon text-info">
            <Icon name="zap" :size="20" />
          </div>
          <h3 class="trust-title">Self-Healing Reliability</h3>
          <p class="trust-desc">
            Equipped with autonomous error recovery. If an initial query pattern is imperfect, the system auto-corrects and falls back to deterministic engines, ensuring 100% dependable uptime.
          </p>
        </div>
      </div>
    </section>

    <!-- Section 5: Frequently Asked Questions (FAQ) -->
    <section class="content-section faq-section">
      <div class="section-header-block">
        <span class="section-tag font-mono">KNOWLEDGE BASE</span>
        <h2 class="section-heading">Frequently Asked Questions</h2>
        <p class="section-lead">
          Everything you need to know about how SubscriptIQ manages your subscriptions and saves your company money.
        </p>
      </div>

      <div class="faq-accordion-list">
        <div
          v-for="(faq, idx) in faqList"
          :key="idx"
          class="faq-item"
          :class="{ 'is-open': openFaqIndices.includes(idx) }"
          @click="toggleFaq(idx)"
        >
          <div class="faq-question-row">
            <div class="faq-q-text">
              <span class="faq-q-badge font-mono">Q{{ idx + 1 }}</span>
              <span class="faq-q-title">{{ faq.q }}</span>
            </div>
            <button class="faq-toggle-btn" :aria-label="openFaqIndices.includes(idx) ? 'Collapse question' : 'Expand question'">
              <Icon :name="openFaqIndices.includes(idx) ? 'chevron-up' : 'chevron-down'" :size="15" />
            </button>
          </div>

          <div v-show="openFaqIndices.includes(idx)" class="faq-answer-body">
            <p>{{ faq.a }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer Banner -->
    <footer class="about-footer-card">
      <div class="footer-sparkle-beacon">
        <Icon name="sparkles" :size="24" />
      </div>
      <div class="footer-cta-text">
        <h3 class="footer-cta-title">Ready to take control of your organization's software subscriptions?</h3>
        <p class="footer-cta-sub">
          Ask SubscriptIQ AI a question right now, or explore active tools and optimizations on the dashboard.
        </p>
      </div>
      <div class="footer-buttons">
        <button class="primary-cta-btn" @click="uiStore.setActiveNav('dashboard')">
          <Icon name="dashboard" :size="14" />
          <span>Open Dashboard</span>
        </button>
        <button class="secondary-cta-btn" @click="uiStore.toggleChat">
          <Icon name="sparkles" :size="14" />
          <span>Launch AI Assistant</span>
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useChatStore } from '@/stores/chat'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()
const chatStore = useChatStore()

// --- Core Enterprise Capabilities ---
const enterpriseFeatures = [
  {
    category: 'COST OPTIMIZATION',
    title: 'Automated License Waste Reclamation',
    description: 'Cross-references employee login activity to flag dormant seats (>30 days inactive) and unallocated licenses, calculating exact monthly dollar waste so you can downsize before renewing.',
    sampleQuery: 'Find all dormant license seats',
    icon: 'target',
    color: '#f59e0b',
    bg: 'rgba(245, 158, 11, 0.12)'
  },
  {
    category: 'CONTRACT RADAR',
    title: 'Proactive Renewal & Horizon Tracking',
    description: 'Never get blindsided by auto-renewal terms again. Track contracts expiring in the next 14, 30, or 60 days to renegotiate terms or cancel unused services ahead of vendor lock-ins.',
    sampleQuery: 'Which subscriptions renew in the next 30 days?',
    icon: 'dashboard',
    color: '#10b981',
    bg: 'rgba(16, 185, 129, 0.12)'
  },
  {
    category: 'ONE-CLICK AUDIT',
    title: 'Instant 360° Subscription Audits',
    description: 'Click "Audit" on any subscription in your dashboard to immediately see licensed capacity, assigned headcount, true cost per active user, and exact optimizable spend.',
    sampleQuery: 'Audit AWS Compute & RDS Suite subscription metrics',
    icon: 'analytics',
    color: '#8b5cf6',
    bg: 'rgba(139, 92, 246, 0.12)'
  },
  {
    category: 'SPEND INTELLIGENCE',
    title: 'Departmental & Vendor Spend Breakdown',
    description: 'Instantly view where your software budget is flowing across Engineering, Sales, Marketing, and Operations. Track monthly costs and annual contract commitments on demand.',
    sampleQuery: 'Show total monthly spend by category',
    icon: 'credit-card',
    color: '#38bdf8',
    bg: 'rgba(56, 189, 248, 0.12)'
  },
  {
    category: 'PEOPLE & LICENSES',
    title: 'Employee Tool Allocation & Painless Offboarding',
    description: 'Know exactly which software tools any employee holds. Ensure team members have the right tiers and effortlessly verify that licenses are reclaimed when staff depart.',
    sampleQuery: 'What subscriptions does Elena Wilson have',
    icon: 'users',
    color: '#06b6d4',
    bg: 'rgba(6, 182, 212, 0.12)'
  },
  {
    category: 'BILLING COMPLIANCE',
    title: 'Invoice Tracking & Vendor Risk Management',
    description: 'Monitor pending or overdue bills and review vendor compliance ratings (SOC2, FedRAMP, HIPAA) to protect corporate data and ensure vendor alignment.',
    sampleQuery: 'Show all pending or overdue invoices',
    icon: 'lock',
    color: '#ec4899',
    bg: 'rgba(236, 72, 153, 0.12)'
  }
]

// --- User Roles & Personas ---
const userRoles = [
  {
    id: 'cfo',
    emoji: '🧑‍💼',
    title: 'CFOs & Finance Directors',
    headline: 'Eliminate SaaS Budget Creep & Stop Runaway Software Costs',
    mission: 'Gain effortless real-time transparency into recurring SaaS expenses across all departments, vendors, and subsidiaries.',
    benefits: [
      {
        title: 'Zero Surprise Bills',
        desc: 'Know your exact monthly and annual software commitments without waiting for accounting reconciliations.'
      },
      {
        title: 'Immediate Dollar Savings',
        desc: 'Quantify exact recoverable waste from unallocated licenses and inactive accounts to reduce recurring software spend by 20-30%.'
      },
      {
        title: 'Board-Ready Reports',
        desc: 'Export clean CSV and JSON reports ready for financial audits, board presentations, and annual department budgeting.'
      }
    ],
    workflow: 'Ask "Total monthly spend by category" or "Show pending invoices" at the beginning of each planning cycle.'
  },
  {
    id: 'it',
    emoji: '💻',
    title: 'IT & DevOps Managers',
    headline: 'Centralize Tool Ownership, License Provisioning & Offboarding',
    mission: 'Prevent redundant software purchases and reclaim unassigned seats before purchasing expensive new accounts.',
    benefits: [
      {
        title: 'Automated Inactivity Tracking',
        desc: 'Instantly identify accounts with zero login activity in over 30 days and reassign them to incoming team members.'
      },
      {
        title: 'One-Click Tool Audits',
        desc: 'Audit infrastructure services like AWS, GitHub, or Datadog to check capacity utilization and per-user cost.'
      },
      {
        title: 'Seamless Employee Offboarding',
        desc: 'Instantly look up all software tools held by departing employees to ensure complete license recovery and access revocation.'
      }
    ],
    workflow: 'Use the Dashboard Audit button to check capacity vs actual user activity before purchasing new licenses.'
  },
  {
    id: 'procurement',
    emoji: '📋',
    title: 'Procurement & Legal Officers',
    headline: 'Negotiate Contracts from a Position of Data-Backed Strength',
    mission: 'Eliminate auto-renewal lock-ins and leverage actual seat usage data during vendor renegotiations.',
    benefits: [
      {
        title: '30/60/90-Day Renewal Horizon',
        desc: 'Receive proactive alerts weeks before contracts renew so you never miss a cancellation or negotiation window.'
      },
      {
        title: 'Hard Data for Downsizing',
        desc: 'Present vendors with exact dormancy data showing that your team only needs 80 seats instead of 120, cutting contract costs.'
      },
      {
        title: 'Vendor Compliance Verification',
        desc: 'Instantly check vendor security compliance ratings (FedRAMP, SOC2, HIPAA) to maintain organizational compliance.'
      }
    ],
    workflow: 'Ask "Which subscriptions renew in the next 30 days?" weekly to track upcoming vendor milestones.'
  },
  {
    id: 'lead',
    emoji: '👥',
    title: 'Department Leads & Managers',
    headline: 'Equip Your Team with the Right Tools Without Exceeding Budget',
    mission: 'Ensure your engineers, designers, and marketers have the software they need without administrative friction.',
    benefits: [
      {
        title: 'Departmental Budget Mastery',
        desc: 'See how your team’s software expenditure compares against allocated annual budgets in real time.'
      },
      {
        title: 'Team Tool Stack Transparency',
        desc: 'Verify that team members have the appropriate seat tiers (e.g. Figma Editor vs Viewer, GitHub Enterprise).'
      },
      {
        title: 'Self-Service Answers',
        desc: 'Get immediate answers about your team’s tools without waiting days for IT helpdesk tickets.'
      }
    ],
    workflow: 'Ask "Show all users in Engineering" or check software tools allocated to your team.'
  }
]

const activeRoleId = ref('cfo')
const selectedRole = computed(() => {
  return userRoles.find(r => r.id === activeRoleId.value) || userRoles[0]
})

// --- Interactive FAQ Section ---
const openFaqIndices = ref([0, 1])

function toggleFaq(idx) {
  if (openFaqIndices.value.includes(idx)) {
    openFaqIndices.value = openFaqIndices.value.filter(i => i !== idx)
  } else {
    openFaqIndices.value.push(idx)
  }
}

const faqList = [
  {
    q: 'How does SubscriptIQ directly save our company money on software?',
    a: 'Most enterprises overspend by 25-35% on software due to unused licenses, duplicate applications, and auto-renewed contracts. SubscriptIQ cross-references your subscription costs with employee login activity to flag dormant seats (>30 days inactive) and unallocated licenses. This provides your finance and IT teams with exact dollar savings so you can downsize tiers before renewal dates.'
  },
  {
    q: 'How does it identify unused or dormant licenses?',
    a: 'SubscriptIQ monitors last activity telemetry for every provisioned seat. When an assigned user has not logged into an application for over 30 days, the license is flagged as dormant. The system computes the financial waste by multiplying dormant seats by the nominal seat cost, showing you exactly how much money is sitting idle.'
  },
  {
    q: 'Do our team members need any technical or database skills to use it?',
    a: 'None whatsoever! SubscriptIQ is designed for business users, CFOs, IT administrators, and department heads. You interact with it just as you would talk to a colleague in plain English—e.g., "What are our top 5 subscriptions?", "Who has a HubSpot license?", or "Show upcoming renewals". The system translates your question into verified data instantly.'
  },
  {
    q: 'How does SubscriptIQ prevent surprise contract renewals?',
    a: 'SubscriptIQ maintains an active renewal radar that monitors all contract end dates. You can filter upcoming renewals across 14, 30, or 60-day horizons with a single click or chat prompt, allowing your procurement team to open renegotiations or issue cancellation notices well before automatic renewal clauses take effect.'
  },
  {
    q: 'Can we check all software assigned to an employee when they leave?',
    a: 'Yes! During employee offboarding, simply ask "What subscriptions does [Employee Name] have?". SubscriptIQ immediately lists every tool, seat tier, and license allocated to that person, making offboarding and license reclamation seamless and error-free.'
  },
  {
    q: 'Is our corporate financial and employee data secure?',
    a: 'Absolutely. SubscriptIQ operates under strict read-only execution guardrails. It only reads analytical data to generate insights and is architected to make modification or deletion of your corporate database completely impossible. No destructive operations are ever permitted.'
  }
]

function tryQuery(q) {
  chatStore.sendMessage(q)
}
</script>

<style scoped>
.about-view-container {
  flex: 1;
  padding: 32px 40px 60px;
  overflow-y: auto;
  color: var(--text-primary);
  max-width: 1320px;
  margin: 0 auto;
}

/* Hero Section */
.about-hero-section {
  text-align: center;
  max-width: 980px;
  margin: 0 auto 52px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 5px 14px;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.28);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: 0.06em;
  margin-bottom: 20px;
}

.hero-badge-icon {
  color: var(--accent);
}

.hero-title {
  font-size: 34px;
  font-weight: 800;
  line-height: 1.25;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #38bdf8 55%, #c084fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-title-highlight {
  background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline;
}

.hero-subtitle {
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-secondary);
  max-width: 840px;
  margin-bottom: 36px;
}

/* Hero Stats Bar */
.hero-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  width: 100%;
  margin-bottom: 32px;
}

.hero-stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 18px 16px;
  text-align: left;
  transition: transform var(--transition-fast), border-color var(--transition-fast);
}

.hero-stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(56, 189, 248, 0.3);
}

.stat-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.stat-number {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 3px;
}

.stat-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-sub {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.35;
}

.hero-cta-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.primary-cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--accent-gradient);
  border: none;
  border-radius: var(--radius-sm);
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.primary-cta-btn:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

.secondary-cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.secondary-cta-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

/* Content Sections */
.content-section {
  margin-bottom: 56px;
}

.section-header-block {
  text-align: left;
  margin-bottom: 28px;
}

.section-tag {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: 0.08em;
  margin-bottom: 6px;
}

.section-heading {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.section-lead {
  font-size: 14px;
  color: var(--text-secondary);
  max-width: 820px;
  line-height: 1.5;
}

/* Before vs. After Comparison Grid */
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22px;
}

.comparison-card {
  border-radius: var(--radius-md);
  padding: 26px 24px;
  display: flex;
  flex-direction: column;
}

.without-card {
  background: rgba(239, 68, 68, 0.03);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.with-card {
  background: rgba(16, 185, 129, 0.03);
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.card-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  align-self: flex-start;
  margin-bottom: 14px;
}

.without-badge {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.with-badge {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}

.comparison-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 18px;
}

.pain-points-list,
.benefits-points-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pain-points-list li,
.benefits-points-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-secondary);
}

.pain-points-list li strong,
.benefits-points-list li strong {
  color: var(--text-primary);
}

.bullet-cross {
  color: #ef4444;
  font-weight: 700;
  font-size: 14px;
  line-height: 1.2;
}

.bullet-check {
  color: #10b981;
  font-weight: 700;
  font-size: 14px;
  line-height: 1.2;
}

/* Features Mosaic Grid */
.features-mosaic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 20px;
}

.feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 22px 20px;
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-fast), border-color var(--transition-fast);
}

.feature-card:hover {
  transform: translateY(-2px);
  border-color: rgba(56, 189, 248, 0.35);
}

.feature-icon-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.feature-icon-beacon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-badge {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  background: var(--bg-tertiary);
  padding: 2px 7px;
  border-radius: 4px;
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.feature-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 18px;
  flex: 1;
}

.feature-highlight-box {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.highlight-label {
  font-size: 9.5px;
  color: var(--text-muted);
  font-weight: 600;
  letter-spacing: 0.05em;
}

.sample-query-pill {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: transparent;
  border: none;
  padding: 0;
  color: var(--accent);
  font-size: 11.5px;
  font-style: italic;
  cursor: pointer;
  text-align: left;
  transition: opacity var(--transition-fast);
}

.sample-query-pill:hover {
  text-decoration: underline;
  opacity: 0.9;
}

/* Role Based Value Section */
.bg-gradient-panel {
  background: linear-gradient(180deg, rgba(56, 189, 248, 0.03) 0%, rgba(15, 23, 42, 0.0) 100%);
  border: 1px solid rgba(56, 189, 248, 0.12);
  border-radius: var(--radius-lg);
  padding: 32px 30px;
}

.role-tabs-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.role-tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.role-tab-btn:hover {
  color: var(--text-primary);
  border-color: rgba(56, 189, 248, 0.3);
}

.role-tab-btn.is-active {
  background: rgba(56, 189, 248, 0.12);
  border-color: var(--accent);
  color: var(--text-primary);
  font-weight: 600;
}

.role-emoji {
  font-size: 15px;
}

.role-detail-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 26px 24px;
}

.role-card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.role-large-emoji {
  font-size: 36px;
}

.role-title-column {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.role-headline {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.role-mission-statement {
  font-size: 13px;
  color: var(--text-secondary);
}

.role-benefits-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 22px;
}

.benefit-item {
  display: flex;
  gap: 10px;
}

.benefit-check {
  color: var(--success);
  margin-top: 1px;
}

.benefit-name {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.benefit-explanation {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.45;
}

.role-action-footer {
  border-top: 1px solid var(--border-color);
  padding-top: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-note {
  font-size: 10.5px;
  color: var(--text-muted);
  font-weight: 600;
}

.workflow-text {
  font-size: 12.5px;
  color: var(--accent);
}

/* Trust Grid */
.trust-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.trust-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-fast), border-color var(--transition-fast);
}

.trust-card:hover {
  transform: translateY(-2px);
  border-color: rgba(56, 189, 248, 0.3);
}

.trust-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.trust-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.trust-desc {
  font-size: 12.5px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* FAQ Section */
.faq-accordion-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.faq-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: border-color var(--transition-fast);
}

.faq-item:hover {
  border-color: rgba(56, 189, 248, 0.3);
}

.faq-item.is-open {
  border-color: rgba(56, 189, 248, 0.4);
}

.faq-question-row {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.faq-q-text {
  display: flex;
  align-items: center;
  gap: 12px;
}

.faq-q-badge {
  font-size: 11px;
  color: var(--accent);
  background: rgba(56, 189, 248, 0.1);
  padding: 2px 7px;
  border-radius: 4px;
  font-weight: 600;
}

.faq-q-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.faq-toggle-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.faq-answer-body {
  padding: 0 20px 18px 48px;
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-secondary);
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  padding-top: 12px;
}

/* Footer Banner */
.about-footer-card {
  margin-top: 30px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.08) 0%, rgba(14, 165, 233, 0.03) 100%);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: var(--radius-lg);
  padding: 30px 32px;
  display: flex;
  align-items: center;
  gap: 22px;
}

.footer-sparkle-beacon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--accent-gradient);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.footer-cta-text {
  flex: 1;
}

.footer-cta-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.footer-cta-sub {
  font-size: 13px;
  color: var(--text-secondary);
}

.footer-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* =========================================================
   Light Mode Theme Enhancements & High Contrast Styles
   ========================================================= */
[data-theme="light"] .hero-title {
  background: linear-gradient(135deg, #0f172a 0%, #0369a1 40%, #4338ca 75%, #6d28d9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

[data-theme="light"] .hero-title-highlight {
  background: linear-gradient(135deg, #0284c7 0%, #4f46e5 50%, #7c3aed 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

[data-theme="light"] .hero-badge {
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%);
  border: 1px solid rgba(2, 132, 199, 0.25);
  color: #0284c7;
}

[data-theme="light"] .hero-subtitle {
  color: #334155;
}

[data-theme="light"] .hero-stat-card {
  background: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}

[data-theme="light"] .hero-stat-card:hover {
  border-color: #0284c7;
  box-shadow: 0 4px 16px rgba(2, 132, 199, 0.12);
}

[data-theme="light"] .stat-icon-wrap {
  background: #f1f5f9;
}

[data-theme="light"] .stat-number {
  color: #0f172a;
}

[data-theme="light"] .stat-label {
  color: #1e293b;
}

[data-theme="light"] .stat-sub {
  color: #475569;
}

[data-theme="light"] .section-tag {
  color: #0284c7;
  background: rgba(2, 132, 199, 0.08);
  padding: 3px 10px;
  border-radius: 4px;
  border: 1px solid rgba(2, 132, 199, 0.18);
}

[data-theme="light"] .section-heading {
  color: #0f172a;
}

[data-theme="light"] .section-lead {
  color: #334155;
}

/* Comparison Cards */
[data-theme="light"] .without-card {
  background: #fff5f5;
  border: 1px solid #fca5a5;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.05);
}

[data-theme="light"] .without-badge {
  background: #fee2e2;
  color: #b91c1c;
}

[data-theme="light"] .with-card {
  background: #f0fdf4;
  border: 1px solid #86efac;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.05);
}

[data-theme="light"] .with-badge {
  background: #dcfce7;
  color: #15803d;
}

[data-theme="light"] .comparison-title {
  color: #0f172a;
}

[data-theme="light"] .pain-points-list li,
[data-theme="light"] .benefits-points-list li {
  color: #334155;
}

[data-theme="light"] .pain-points-list li strong,
[data-theme="light"] .benefits-points-list li strong {
  color: #0f172a;
}

/* Feature Cards */
[data-theme="light"] .feature-card {
  background: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}

[data-theme="light"] .feature-card:hover {
  border-color: #0284c7;
  box-shadow: 0 6px 20px rgba(2, 132, 199, 0.12);
}

[data-theme="light"] .feature-title {
  color: #0f172a;
}

[data-theme="light"] .feature-description {
  color: #334155;
}

[data-theme="light"] .feature-badge {
  background: #f1f5f9;
  color: #0284c7;
  border: 1px solid #e2e8f0;
}

[data-theme="light"] .feature-highlight-box {
  background: #f8fafc;
  border-color: #e2e8f0;
}

[data-theme="light"] .highlight-label {
  color: #475569;
}

[data-theme="light"] .sample-query-pill {
  color: #0284c7;
}

/* Role Panel */
[data-theme="light"] .bg-gradient-panel {
  background: linear-gradient(180deg, rgba(2, 132, 199, 0.04) 0%, rgba(248, 250, 252, 0.6) 100%);
  border-color: #e2e8f0;
}

[data-theme="light"] .role-tab-btn {
  background: #ffffff;
  border-color: #e2e8f0;
  color: #475569;
}

[data-theme="light"] .role-tab-btn:hover {
  color: #0f172a;
  border-color: #0284c7;
}

[data-theme="light"] .role-tab-btn.is-active {
  background: #eff6ff;
  border-color: #0284c7;
  color: #0284c7;
}

[data-theme="light"] .role-detail-card {
  background: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}

[data-theme="light"] .role-headline {
  color: #0f172a;
}

[data-theme="light"] .role-mission-statement {
  color: #334155;
}

[data-theme="light"] .benefit-name {
  color: #0f172a;
}

[data-theme="light"] .benefit-explanation {
  color: #334155;
}

[data-theme="light"] .role-action-footer {
  border-color: #e2e8f0;
}

[data-theme="light"] .footer-note {
  color: #475569;
}

[data-theme="light"] .workflow-text {
  color: #0284c7;
}

/* Trust Grid */
[data-theme="light"] .trust-card {
  background: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}

[data-theme="light"] .trust-card:hover {
  border-color: #0284c7;
  box-shadow: 0 6px 20px rgba(2, 132, 199, 0.12);
}

[data-theme="light"] .trust-icon {
  background: #f1f5f9;
}

[data-theme="light"] .trust-title {
  color: #0f172a;
}

[data-theme="light"] .trust-desc {
  color: #334155;
}

/* FAQ */
[data-theme="light"] .faq-item {
  background: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.03);
}

[data-theme="light"] .faq-item:hover,
[data-theme="light"] .faq-item.is-open {
  border-color: #0284c7;
}

[data-theme="light"] .faq-q-badge {
  background: rgba(2, 132, 199, 0.1);
  color: #0284c7;
}

[data-theme="light"] .faq-q-title {
  color: #0f172a;
}

[data-theme="light"] .faq-toggle-btn {
  color: #475569;
}

[data-theme="light"] .faq-answer-body {
  color: #334155;
  border-top-color: #f1f5f9;
}

/* Footer Banner */
[data-theme="light"] .about-footer-card {
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.08) 0%, rgba(99, 102, 241, 0.06) 100%);
  border-color: rgba(2, 132, 199, 0.28);
  box-shadow: 0 4px 20px rgba(2, 132, 199, 0.08);
}

[data-theme="light"] .footer-cta-title {
  color: #0f172a;
}

[data-theme="light"] .footer-cta-sub {
  color: #334155;
}

[data-theme="light"] .secondary-cta-btn {
  background: #ffffff;
  border-color: #cbd5e1;
  color: #0f172a;
}

[data-theme="light"] .secondary-cta-btn:hover {
  border-color: #0284c7;
  color: #0284c7;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .hero-stats-grid,
  .comparison-grid,
  .trust-grid {
    grid-template-columns: 1fr;
  }
  .role-benefits-grid {
    grid-template-columns: 1fr;
  }
  .about-footer-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
