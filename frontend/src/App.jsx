import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  `${window.location.protocol}//${window.location.hostname}:5050`;

const navSections = [
  {
    items: [{ label: "Dashboard", icon: "dashboard", isActive: true }],
  },
  {
    title: "Analysis",
    items: [
      { label: "Analytics", icon: "analytics" },
      { label: "Trends", icon: "trends" },
    ],
  },
  {
    title: "Insights",
    items: [
      { label: "Distribution", icon: "distribution" },
      { label: "AI Insights", icon: "insights" },
      { label: "Customers", icon: "customers" },
    ],
  },
];

const fallbackSummary = {
  asOfDate: "2026-09-09",
  dataset: {
    name: "synthetic_energy_customer_sites.csv",
    grain: "One site-level contract episode per row",
    businessPartners: 100000,
    sites: 626767,
    episodes: 992631,
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
  const [health, setHealth] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");
  const [summaryError, setSummaryError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [healthResult, summaryResult] = await Promise.allSettled([
          fetch(`${API_BASE_URL}/api/health`),
          fetch(`${API_BASE_URL}/api/dashboard/summary`),
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
  }, []);

  const dashboardSummary = summary || fallbackSummary;
  const { dataset, kpis, mixes, trends } = dashboardSummary;
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
      percentage: 100 - kpis.activeSiteRate,
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
                  className={`nav-item${item.isActive ? " nav-item-active" : ""}`}
                  key={item.label}
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
            <p className="eyebrow">Executive Summary</p>
            <h1 id="page-title">Dashboard</h1>
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
            </div>

            <div className="filter-group">
              <button className="filter-button filter-button-active" type="button">
                Current portfolio
              </button>
              <button className="filter-button" type="button">
                All channels
              </button>
              <button className="filter-button" type="button">
                All commodities
              </button>
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

            <article className="panel insight-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">Focus</p>
                  <h3>Executive Actions</h3>
                </div>
              </div>
              <div className="action-list">
                <div>
                  <span className="action-dot action-dot-red" />
                  <p>Review churn-heavy channels before renewal planning.</p>
                </div>
                <div>
                  <span className="action-dot action-dot-amber" />
                  <p>Track leakage by same-day and five-day drops.</p>
                </div>
                <div>
                  <span className="action-dot action-dot-green" />
                  <p>Move non-digital business partners into portal adoption campaigns.</p>
                </div>
              </div>
              <div className="data-footnote">
                <span>Dataset grain</span>
                <strong>{dataset.grain}</strong>
              </div>
            </article>
          </section>
        </div>
      </section>
    </main>
  );
}

export default App;
