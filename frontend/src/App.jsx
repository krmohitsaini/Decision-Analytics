import { useEffect, useState } from "react";
import "./App.css";
import AgentChannelDeepDive from "./pages/AgentChannelDeepDive.jsx";
import CommercialPerformance from "./pages/CommercialPerformance.jsx";
import CustomerSitePortfolio from "./pages/CustomerSitePortfolio.jsx";
import DataQuality from "./pages/DataQuality.jsx";
import DigitalEngagement from "./pages/DigitalEngagement.jsx";
import ProductPlanAdoption from "./pages/ProductPlanAdoption.jsx";
import RetentionDeepDive from "./pages/RetentionDeepDive.jsx";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  `${window.location.protocol}//${window.location.hostname}:5050`;

const navSections = [
  {
    items: [{ key: "dashboard", label: "Dashboard", icon: "dashboard" }],
  },
  {
    title: "Analysis",
    items: [
      { key: "retention", label: "Retention Deep Dive", icon: "analytics" },
      { key: "commercial", label: "Commercial Performance", icon: "trends" },
      { key: "portfolio", label: "Customer & Site Portfolio", icon: "distribution" },
      { key: "products", label: "Product and Plan Adoption", icon: "app" },
      { key: "digital", label: "Digital Engagement", icon: "insights" },
      { key: "agents", label: "Agent and Channel Deep Dive", icon: "customers" },
      { key: "quality", label: "Data Quality", icon: "dashboard" },
    ],
  },
];

const defaultFilters = {
  scope: "current",
  channel: "",
  commodity: "",
};

const analysisPageComponents = {
  retention: RetentionDeepDive,
  commercial: CommercialPerformance,
  portfolio: CustomerSitePortfolio,
  products: ProductPlanAdoption,
  digital: DigitalEngagement,
  agents: AgentChannelDeepDive,
  quality: DataQuality,
};

const fallbackSummary = {
  asOfDate: "2026-09-09",
  dataset: {
    name: "synthetic_energy_customer_sites.csv",
    sourceType: "csv",
    grain: "One site-level contract episode per row",
    businessPartners: 100000,
    sites: 626767,
    episodes: 992631,
  },
  filters: {
    scope: "current",
    channel: "",
    commodity: "",
    availableScopes: [
      { label: "Current portfolio", value: "current" },
      { label: "All contract episodes", value: "all" },
    ],
    channels: [
      { label: "Broker", count: 91241 },
      { label: "Digital", count: 125551 },
      { label: "Direct Sale", count: 160539 },
      { label: "Door-to-Door", count: 59691 },
      { label: "Field Sales", count: 58950 },
      { label: "IBTS", count: 137857 },
      { label: "Partner", count: 72050 },
      { label: "Referral", count: 72291 },
      { label: "Retail Kiosk", count: 20353 },
      { label: "Telesales", count: 214108 },
    ],
    commodities: [
      { label: "BOTH", count: 228441 },
      { label: "ELE", count: 416793 },
      { label: "GAS", count: 347397 },
    ],
  },
  kpis: {
    totalBusinessPartners: 100000,
    totalSites: 626767,
    totalContractEpisodes: 992631,
    activeSites: 323710,
    activeBusinessPartners: 94329,
    activeSiteRate: 51.6,
    churnRate: 42.6,
    renewalRate: 44.6,
    leakageRate: 2.1,
    digitalAdoptionRate: 29.9,
    averageSitesPerBusinessPartner: 6.27,
    dobCaptureRate: 72.1,
  },
  mixes: {
    channels: [
      { label: "Telesales", count: 214108, percentage: 21.6 },
      { label: "Direct Sale", count: 160539, percentage: 16.2 },
      { label: "IBTS", count: 137857, percentage: 13.9 },
      { label: "Digital", count: 125551, percentage: 12.6 },
      { label: "Broker", count: 91241, percentage: 9.2 },
      { label: "Referral", count: 72291, percentage: 7.3 },
    ],
    outcomes: [
      { label: "Active", count: 323710, percentage: 32.6 },
      { label: "Churn", count: 285177, percentage: 28.7 },
      { label: "Auto Renewal", count: 161672, percentage: 16.3 },
      { label: "Positive Renewal", count: 136709, percentage: 13.8 },
      { label: "TOS", count: 64659, percentage: 6.5 },
      { label: "Leakage", count: 20704, percentage: 2.1 },
    ],
    commodities: [
      { label: "ELE", count: 416793, percentage: 42 },
      { label: "GAS", count: 347397, percentage: 35 },
      { label: "BOTH", count: 228441, percentage: 23 },
    ],
  },
  trends: {
    monthlyStarts: [
      { month: "2025-10", episodes: 31262 },
      { month: "2025-11", episodes: 32997 },
      { month: "2025-12", episodes: 37946 },
      { month: "2026-01", episodes: 41331 },
      { month: "2026-02", episodes: 41824 },
      { month: "2026-03", episodes: 51612 },
      { month: "2026-04", episodes: 57134 },
      { month: "2026-05", episodes: 68306 },
      { month: "2026-06", episodes: 77662 },
      { month: "2026-07", episodes: 94967 },
      { month: "2026-08", episodes: 108280 },
      { month: "2026-09", episodes: 21891 },
    ],
  },
};

function NavIcon({ name }) {
  const icons = {
    dashboard: (
      <>
        <path d="M4 10.5 12 4l8 6.5" />
        <path d="M6.5 10v8h11v-8" />
        <path d="M10 18v-5h4v5" />
      </>
    ),
    analytics: (
      <>
        <path d="M5 19V9" />
        <path d="M12 19V5" />
        <path d="M19 19v-7" />
      </>
    ),
    trends: (
      <>
        <path d="M4 16.5 9 11l4 3 7-8" />
        <path d="M16 6h4v4" />
      </>
    ),
    distribution: (
      <>
        <path d="M12 3v9h9" />
        <path d="M20.4 15A8.5 8.5 0 1 1 9 3.6" />
      </>
    ),
    insights: (
      <>
        <path d="M9 18h6" />
        <path d="M10 22h4" />
        <path d="M8.5 14.5a6 6 0 1 1 7 0c-.9.7-1.5 1.8-1.5 3H10c0-1.2-.6-2.3-1.5-3Z" />
      </>
    ),
    customers: (
      <>
        <path d="M16 19c0-2.2-1.8-4-4-4s-4 1.8-4 4" />
        <path d="M12 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" />
      </>
    ),
    app: (
      <>
        <path d="M8 4h8a4 4 0 0 1 4 4v8a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4V8a4 4 0 0 1 4-4Z" />
        <path d="M8 9h8" />
        <path d="M8 13h5" />
      </>
    ),
  };

  return (
    <svg
      aria-hidden="true"
      className="nav-icon"
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      viewBox="0 0 24 24"
    >
      {icons[name]}
    </svg>
  );
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-US").format(value || 0);
}

function formatPercent(value) {
  return `${Number(value || 0).toFixed(1)}%`;
}

function compactNumber(value) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: value >= 1000000 ? 1 : 0,
    notation: "compact",
  }).format(value || 0);
}

function buildDashboardSummaryUrl(filters) {
  const params = new URLSearchParams();

  params.set("scope", filters.scope);

  if (filters.channel) {
    params.set("channel", filters.channel);
  }

  if (filters.commodity) {
    params.set("commodity", filters.commodity);
  }

  return `${API_BASE_URL}/api/dashboard/summary?${params.toString()}`;
}

function buildDashboardInsightsUrl(filters) {
  const params = new URLSearchParams();

  params.set("scope", filters.scope);

  if (filters.channel) {
    params.set("channel", filters.channel);
  }

  if (filters.commodity) {
    params.set("commodity", filters.commodity);
  }

  return `${API_BASE_URL}/api/dashboard/insights?${params.toString()}`;
}

function buildBaselineInsights(summary) {
  const kpis = summary.kpis || {};
  const mixes = summary.mixes || {};
  const topChannel = mixes.channels?.[0]?.label || "The leading channel";
  const topOutcome = mixes.outcomes?.[0]?.label || "The leading outcome";

  return {
    summary: `Portfolio health is anchored by a ${formatPercent(
      kpis.activeSiteRate,
    )} active site rate, with churn at ${formatPercent(
      kpis.churnRate,
    )} and digital adoption at ${formatPercent(kpis.digitalAdoptionRate)}.`,
    drivers: [
      `${topChannel} is the largest visible channel in the selected view.`,
      `${topOutcome} is the largest visible contract outcome in the selected view.`,
      `Digital adoption is ${formatPercent(
        kpis.digitalAdoptionRate,
      )} across distinct business partners.`,
    ],
    risks: [
      `Churn is ${formatPercent(kpis.churnRate)} of closed contract episodes.`,
      `Leakage is ${formatPercent(kpis.leakageRate)} of selected contract episodes.`,
    ],
    actions: [
      "Prioritize churn review by channel before renewal planning.",
      "Inspect leakage cases by same-day and early-life drops.",
      "Target non-digital business partners for portal adoption campaigns.",
    ],
    caveats: ["These baseline insights are deterministic and do not use an LLM."],
  };
}

function InsightGroup({ title, items }) {
  if (!items?.length) {
    return null;
  }

  return (
    <div className="insight-group">
      <p>{title}</p>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function CopilotIcon() {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      viewBox="0 0 24 24"
    >
      <path d="M12 3v3" />
      <path d="M12 18v3" />
      <path d="m4.9 4.9 2.1 2.1" />
      <path d="m17 17 2.1 2.1" />
      <path d="M3 12h3" />
      <path d="M18 12h3" />
      <path d="m4.9 19.1 2.1-2.1" />
      <path d="m17 7 2.1-2.1" />
      <path d="M9 12a3 3 0 1 0 6 0 3 3 0 0 0-6 0Z" />
    </svg>
  );
}

function KpiCard({ label, value, helper, tone = "neutral" }) {
  return (
    <article className={`kpi-card kpi-card-${tone}`}>
      <p>{label}</p>
      <strong>{value}</strong>
      <span>{helper}</span>
    </article>
  );
}

function BarList({ items, formatter = formatNumber }) {
  const maxValue = Math.max(...items.map((item) => item.count), 1);

  if (!items.length) {
    return <p className="empty-state">Connect the dashboard API to load mix details.</p>;
  }

  return (
    <div className="bar-list">
      {items.map((item) => (
        <div className="bar-row" key={item.label}>
          <div className="bar-row-label">
            <span>{item.label}</span>
            <strong>{formatter(item.count)}</strong>
          </div>
          <div className="bar-track" aria-hidden="true">
            <span style={{ width: `${Math.max((item.count / maxValue) * 100, 5)}%` }} />
          </div>
          <small>{formatPercent(item.percentage)}</small>
        </div>
      ))}
    </div>
  );
}

function MonthlyStarts({ items }) {
  const maxValue = Math.max(...items.map((item) => item.episodes), 1);

  if (!items.length) {
    return <p className="empty-state">Monthly start trend will appear when the API is online.</p>;
  }

  return (
    <div className="trend-chart" aria-label="Monthly contract starts">
      {items.map((item) => (
        <div className="trend-column" key={item.month}>
          <div className="trend-bar">
            <span style={{ height: `${Math.max((item.episodes / maxValue) * 100, 8)}%` }} />
          </div>
          <small>{item.month.slice(5)}</small>
        </div>
      ))}
    </div>
  );
}

function App() {
  const [selectedPage, setSelectedPage] = useState("dashboard");
  const [health, setHealth] = useState(null);
  const [summary, setSummary] = useState(null);
  const [filters, setFilters] = useState(defaultFilters);
  const [error, setError] = useState("");
  const [summaryError, setSummaryError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [llmConfig, setLlmConfig] = useState(null);
  const [baselineInsights, setBaselineInsights] = useState(null);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [llmInsights, setLlmInsights] = useState(null);
  const [llmError, setLlmError] = useState("");
  const [isLlmLoading, setIsLlmLoading] = useState(false);
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [isQuestionLoading, setIsQuestionLoading] = useState(false);

  useEffect(() => {
    async function loadDashboard() {
      setIsLoading(true);
      setSummaryError("");

      try {
        const [healthResult, summaryResult] = await Promise.allSettled([
          fetch(`${API_BASE_URL}/api/health`),
          fetch(buildDashboardSummaryUrl(filters)),
        ]);

        if (healthResult.status === "fulfilled" && healthResult.value.ok) {
          setHealth(await healthResult.value.json());
        } else {
          setError("Unable to reach backend");
        }

        if (summaryResult.status === "fulfilled" && summaryResult.value.ok) {
          setSummary(await summaryResult.value.json());
        } else {
          setSummaryError("Using bundled CSV baseline until the dashboard API responds.");
          setSummary(fallbackSummary);
        }
      } catch {
        setError("Unable to reach backend");
        setSummaryError("Using bundled CSV baseline until the dashboard API responds.");
        setSummary(fallbackSummary);
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboard();
  }, [filters]);

  useEffect(() => {
    async function loadLlmConfig() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/llm/config`);
        if (response.ok) {
          setLlmConfig(await response.json());
        }
      } catch {
        setLlmConfig(null);
      }
    }

    loadLlmConfig();
  }, []);

  useEffect(() => {
    async function loadBaselineInsights() {
      try {
        const response = await fetch(buildDashboardInsightsUrl(filters));
        if (response.ok) {
          const payload = await response.json();
          setBaselineInsights(payload.insights);
        }
      } catch {
        setBaselineInsights(null);
      }
    }

    loadBaselineInsights();
    setLlmInsights(null);
    setLlmError("");
    setChatMessages([]);
  }, [filters]);

  const dashboardSummary = summary || fallbackSummary;
  const { dataset, kpis, mixes, trends } = dashboardSummary;
  const availableFilters = dashboardSummary.filters || fallbackSummary.filters;
  const activeSitesGap = Math.max(kpis.totalSites - kpis.activeSites, 0);
  const portfolioItems = [
    {
      label: "Active sites",
      count: kpis.activeSites,
      percentage: kpis.activeSiteRate,
    },
    {
      label: "Inactive / closed sites",
      count: activeSitesGap,
      percentage: kpis.totalSites ? 100 - kpis.activeSiteRate : 0,
    },
  ];
  const executiveKpis = [
    {
      label: "Business partners",
      value: formatNumber(kpis.totalBusinessPartners),
      helper: `${formatNumber(kpis.activeBusinessPartners)} with active sites`,
      tone: "blue",
    },
    {
      label: "Active site rate",
      value: formatPercent(kpis.activeSiteRate),
      helper: `${formatNumber(kpis.activeSites)} of ${formatNumber(kpis.totalSites)} sites`,
      tone: "green",
    },
    {
      label: "Churn rate",
      value: formatPercent(kpis.churnRate),
      helper: "Closed contract episodes",
      tone: "red",
    },
    {
      label: "Renewal rate",
      value: formatPercent(kpis.renewalRate),
      helper: "Auto and positive renewals",
      tone: "amber",
    },
    {
      label: "Leakage rate",
      value: formatPercent(kpis.leakageRate),
      helper: "Same-day or near-start drops",
      tone: "violet",
    },
    {
      label: "Digital adoption",
      value: formatPercent(kpis.digitalAdoptionRate),
      helper: "Distinct business partners",
      tone: "teal",
    },
  ];
  const filterSummary = [
    filters.scope === "all" ? "All contract episodes" : "Current portfolio",
    filters.channel || "All channels",
    filters.commodity || "All commodities",
  ].join(" / ");
  const currentPageLabel =
    navSections
      .flatMap((section) => section.items)
      .find((item) => item.key === selectedPage)?.label || "Dashboard";

  function updateFilter(name, value) {
    setFilters((currentFilters) => ({
      ...currentFilters,
      [name]: value,
    }));
  }

  async function generateLlmInsights() {
    setIsLlmLoading(true);
    setLlmError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/llm/dashboard-insights`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(filters),
      });
      const payload = await response.json();

      if (!response.ok) {
        setLlmError(payload.error || "Unable to generate LLM insights.");
        return;
      }

      setLlmInsights(payload.insights);
      setLlmConfig(payload.config || llmConfig);
    } catch {
      setLlmError("Unable to reach the backend LLM insights endpoint.");
    } finally {
      setIsLlmLoading(false);
    }
  }

  async function askDashboardQuestion(event) {
    event.preventDefault();

    const question = chatQuestion.trim();
    if (!question) {
      return;
    }

    setIsQuestionLoading(true);
    setLlmError("");
    setChatQuestion("");
    setChatMessages((messages) => [...messages, { role: "user", text: question }]);

    try {
      const response = await fetch(`${API_BASE_URL}/api/llm/dashboard-question`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ...filters, question }),
      });
      const payload = await response.json();

      if (!response.ok) {
        setLlmError(payload.error || "Unable to answer the question.");
        return;
      }

      setLlmConfig(payload.config || llmConfig);
      setChatMessages((messages) => [
        ...messages,
        {
          role: "assistant",
          answer: payload.answer,
        },
      ]);
    } catch {
      setLlmError("Unable to reach the backend LLM question endpoint.");
    } finally {
      setIsQuestionLoading(false);
    }
  }

  const SelectedAnalysisPage = analysisPageComponents[selectedPage];
  const defaultInsights = baselineInsights || buildBaselineInsights(dashboardSummary);
  const isLlmConfigured = Boolean(llmConfig?.enabled);

  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <div className="brand-row">
          <div className="brand-mark" aria-hidden="true">
            <span />
          </div>
          <span className="brand-name">Decision Analytics</span>
          <button className="sidebar-toggle" type="button" aria-label="Collapse sidebar">
            <NavIcon name="app" />
          </button>
        </div>

        <nav className="sidebar-nav">
          {navSections.map((section) => (
            <div className="nav-section" key={section.title || "primary"}>
              {section.title && <p className="nav-heading">{section.title}</p>}

              {section.items.map((item) => (
                <button
                  className={`nav-item${selectedPage === item.key ? " nav-item-active" : ""}`}
                  key={item.label}
                  onClick={() => setSelectedPage(item.key)}
                  type="button"
                >
                  <NavIcon name={item.icon} />
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          ))}
        </nav>
      </aside>

      <section className="workspace" aria-labelledby="page-title">
        <header className="topbar">
          <div>
            <p className="eyebrow">
              {selectedPage === "dashboard" ? "Executive Summary" : "Analysis"}
            </p>
            <h1 id="page-title">{currentPageLabel}</h1>
          </div>

          <div className="status-pill" aria-live="polite">
            <span
              className={`status-dot${
                !isLoading && error ? " status-dot-error" : ""
              }`}
            />
            {isLoading && "Checking backend"}
            {!isLoading && error && "Backend offline"}
            {!isLoading && health && health.message}
          </div>
        </header>

        {selectedPage === "dashboard" ? (
        <div className="dashboard-page">
          <section className="dashboard-command-row" aria-label="Dashboard filters">
            <div className="dashboard-copy">
              <p className="eyebrow">Energy Customer Sites</p>
              <h2>Portfolio health as of {dashboardSummary.asOfDate}</h2>
              <p>
                {formatNumber(dataset.episodes)} contract episodes across{" "}
                {formatNumber(dataset.sites)} sites and{" "}
                {formatNumber(dataset.businessPartners)} business partners.
              </p>
              <p className="active-filter-line">{filterSummary}</p>
            </div>

            <div className="filter-group" aria-label="Dashboard filters">
              <label className="filter-control">
                <span>Scope</span>
                <select
                  value={filters.scope}
                  onChange={(event) => updateFilter("scope", event.target.value)}
                >
                  {availableFilters.availableScopes.map((scope) => (
                    <option key={scope.value} value={scope.value}>
                      {scope.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="filter-control">
                <span>Channel</span>
                <select
                  value={filters.channel}
                  onChange={(event) => updateFilter("channel", event.target.value)}
                >
                  <option value="">All channels</option>
                  {availableFilters.channels.map((channel) => (
                    <option key={channel.label} value={channel.label}>
                      {channel.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="filter-control">
                <span>Commodity</span>
                <select
                  value={filters.commodity}
                  onChange={(event) => updateFilter("commodity", event.target.value)}
                >
                  <option value="">All commodities</option>
                  {availableFilters.commodities.map((commodity) => (
                    <option key={commodity.label} value={commodity.label}>
                      {commodity.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </section>

          {summaryError && <div className="data-alert">{summaryError}</div>}

          <section className="kpi-grid" aria-label="Executive KPIs">
            {executiveKpis.map((kpi) => (
              <KpiCard key={kpi.label} {...kpi} />
            ))}
          </section>

          <section className="dashboard-grid">
            <article className="panel panel-large">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">Contract Starts</p>
                  <h3>Last 12 Months</h3>
                </div>
                <strong>{compactNumber(kpis.totalContractEpisodes)}</strong>
              </div>
              <MonthlyStarts items={trends.monthlyStarts} />
            </article>

            <article className="panel">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">Portfolio</p>
                  <h3>Site Status</h3>
                </div>
                <strong>{formatPercent(kpis.activeSiteRate)}</strong>
              </div>
              <BarList items={portfolioItems} formatter={compactNumber} />
            </article>

            <article className="panel">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">Outcomes</p>
                  <h3>Contract Mix</h3>
                </div>
                <strong>{formatPercent(kpis.churnRate)}</strong>
              </div>
              <BarList items={mixes.outcomes} formatter={compactNumber} />
            </article>

            <article className="panel">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">Sales</p>
                  <h3>Channel Mix</h3>
                </div>
                <strong>{mixes.channels[0]?.label || "Pending"}</strong>
              </div>
              <BarList items={mixes.channels} formatter={compactNumber} />
            </article>

            <article className="panel">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">Commodity</p>
                  <h3>Episode Mix</h3>
                </div>
                <strong>{formatNumber(kpis.averageSitesPerBusinessPartner)}</strong>
              </div>
              <BarList items={mixes.commodities} formatter={compactNumber} />
            </article>

            <article className="panel insight-panel baseline-insight-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">Baseline Insights</p>
                  <h3>Executive Actions</h3>
                </div>
              </div>

              <div className="insight-content baseline-content">
                <p className="insight-summary">{defaultInsights.summary}</p>
                <InsightGroup title="Drivers" items={defaultInsights.drivers} />
                <InsightGroup title="Risks" items={defaultInsights.risks} />
                <InsightGroup title="Actions" items={defaultInsights.actions} />
              </div>

              <div className="data-footnote">
                <span>Insight mode</span>
                <strong>{defaultInsights.caveats?.[0] || dataset.grain}</strong>
              </div>
            </article>
          </section>
        </div>
        ) : (
          <SelectedAnalysisPage />
        )}
      </section>

      {selectedPage === "dashboard" && (
        <>
          <button
            className="copilot-fab"
            onClick={() => setIsCopilotOpen((isOpen) => !isOpen)}
            type="button"
            aria-label="Open LLM copilot"
          >
            <CopilotIcon />
          </button>

          {isCopilotOpen && (
            <aside className="copilot-popover" aria-label="LLM copilot">
              <div className="copilot-header">
                <div>
                  <p className="panel-kicker">LLM Copilot</p>
                  <h3>Ask the Dashboard</h3>
                </div>
                <button
                  className="copilot-close"
                  onClick={() => setIsCopilotOpen(false)}
                  type="button"
                  aria-label="Close LLM copilot"
                >
                  X
                </button>
              </div>

              <div className={`copilot-status${isLlmConfigured ? "" : " copilot-status-muted"}`}>
                <span>{isLlmConfigured ? "Connected" : "Not configured"}</span>
                <strong>
                  {isLlmConfigured
                    ? `${llmConfig.providerLabel} / ${llmConfig.model}`
                    : "Set LLM_PROVIDER and key in backend/.env"}
                </strong>
              </div>

              <button
                className="copilot-generate"
                disabled={!isLlmConfigured || isLlmLoading}
                onClick={generateLlmInsights}
                type="button"
              >
                {isLlmLoading ? "Generating" : "Generate LLM Insights"}
              </button>

              {llmError && <div className="copilot-error">{llmError}</div>}

              {llmInsights && (
                <div className="copilot-section">
                  <p className="insight-summary">{llmInsights.summary}</p>
                  <InsightGroup title="Drivers" items={llmInsights.drivers} />
                  <InsightGroup title="Risks" items={llmInsights.risks} />
                  <InsightGroup title="Actions" items={llmInsights.actions} />
                </div>
              )}

              <div className="copilot-chat">
                {chatMessages.map((message, index) => (
                  <div
                    className={`chat-message chat-message-${message.role}`}
                    key={`${message.role}-${index}`}
                  >
                    {message.text && <p>{message.text}</p>}
                    {message.answer && (
                      <>
                        <p>{message.answer.answer}</p>
                        <InsightGroup title="Supporting Metrics" items={message.answer.supportingMetrics} />
                        <InsightGroup title="Caveats" items={message.answer.caveats} />
                      </>
                    )}
                  </div>
                ))}
              </div>

              <form className="copilot-form" onSubmit={askDashboardQuestion}>
                <input
                  disabled={!isLlmConfigured || isQuestionLoading}
                  onChange={(event) => setChatQuestion(event.target.value)}
                  placeholder="Question about this dashboard"
                  value={chatQuestion}
                />
                <button
                  disabled={!isLlmConfigured || isQuestionLoading || !chatQuestion.trim()}
                  type="submit"
                >
                  {isQuestionLoading ? "..." : "Ask"}
                </button>
              </form>
            </aside>
          )}
        </>
      )}
    </main>
  );
}

export default App;
