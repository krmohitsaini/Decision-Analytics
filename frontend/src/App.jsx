import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

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
      <section className="status-panel" aria-labelledby="page-title">
        <p className="eyebrow">Decision Analytics POC</p>
        <h1 id="page-title">Flask and React are connected.</h1>
        <p className="description">
          This page is intentionally minimal. It confirms the frontend can call
          the backend before we add data sources, analysis logic, and dashboard
          components.
        </p>

        <div className="status-card" aria-live="polite">
          <span className="status-label">Backend status</span>

          {isLoading && <p className="status-value">Checking connection...</p>}

          {!isLoading && error && (
            <>
              <p className="status-value status-error">Connection failed</p>
              <p className="status-message">{error}</p>
            </>
          )}

          {!isLoading && health && (
            <>
              <p className="status-value status-ok">{health.status}</p>
              <p className="status-message">{health.message}</p>
            </>
          )}
        </div>
      </section>
    </main>
  );
}

export default App;
