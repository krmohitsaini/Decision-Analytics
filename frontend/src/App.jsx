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

function App() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadHealth() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/health`);

        if (!response.ok) {
          throw new Error(`Backend returned ${response.status}`);
        }

        const data = await response.json();
        setHealth(data);
      } catch (err) {
        setError(err.message || "Unable to reach backend");
      } finally {
        setIsLoading(false);
      }
    }

    loadHealth();
  }, []);

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
            <p className="eyebrow">Digital Platform</p>
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

        <div className="placeholder-panel">
          <p className="placeholder-label">Next build area</p>
          <p className="placeholder-title">Dashboard content will come here.</p>
        </div>
      </section>
    </main>
  );
}

export default App;
