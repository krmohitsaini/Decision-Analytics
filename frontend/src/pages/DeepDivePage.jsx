import { useEffect, useState } from "react";


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  `${window.location.protocol}//${window.location.hostname}:5050`;


function formatNumber(value) {
  return new Intl.NumberFormat("en-US").format(value || 0);
}


function formatDecimal(value) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
  }).format(value || 0);
}


function formatValue(value, format) {
  if (typeof value === "string") {
    return value;
  }

  if (format === "percent") {
    return `${Number(value || 0).toFixed(1)}%`;
  }

  if (format === "days") {
    return `${formatDecimal(value)} days`;
  }

  if (format === "decimal") {
    return formatDecimal(value);
  }

  return formatNumber(value);
}


function KpiCard({ label, value, format, helper, tone = "blue" }) {
  return (
    <article className={`kpi-card kpi-card-${tone}`}>
      <p>{label}</p>
      <strong>{formatValue(value, format)}</strong>
      <span>{helper}</span>
    </article>
  );
}


function BarsSection({ section }) {
  const maxValue = Math.max(...section.items.map((item) => item.value), 1);

  return (
    <article className="panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">{section.kicker}</p>
          <h3>{section.title}</h3>
        </div>
        {section.metric && <strong>{section.metric}</strong>}
      </div>
      <div className="bar-list">
        {section.items.map((item) => (
          <div className="bar-row" key={item.label}>
            <div className="bar-row-label">
              <span>{item.label}</span>
              <strong>{formatNumber(item.value)}</strong>
            </div>
            <div className="bar-track" aria-hidden="true">
              <span style={{ width: `${Math.max((item.value / maxValue) * 100, 5)}%` }} />
            </div>
            <small>{Number(item.percentage || 0).toFixed(1)}%</small>
          </div>
        ))}
      </div>
    </article>
  );
}


function TableSection({ section }) {
  return (
    <article className="panel analysis-table-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">{section.kicker}</p>
          <h3>{section.title}</h3>
        </div>
      </div>
      <div className="analysis-table-wrap">
        <table className="analysis-table">
          <thead>
            <tr>
              {section.columns.map((column) => (
                <th key={column.key}>{column.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {section.rows.map((row) => (
              <tr key={row.label}>
                {section.columns.map((column) => (
                  <td key={column.key}>{formatValue(row[column.key], column.format)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}


function SectionRenderer({ section }) {
  if (section.type === "table") {
    return <TableSection section={section} />;
  }

  return <BarsSection section={section} />;
}


function DeepDivePage({ pageKey }) {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadSummary() {
      setIsLoading(true);
      setError("");

      try {
        const response = await fetch(`${API_BASE_URL}/api/analysis/${pageKey}`);

        if (!response.ok) {
          throw new Error(`Analysis API returned ${response.status}`);
        }

        setSummary(await response.json());
      } catch (err) {
        setError(err.message || "Unable to load analysis page");
      } finally {
        setIsLoading(false);
      }
    }

    loadSummary();
  }, [pageKey]);

  if (isLoading) {
    return (
      <div className="analysis-page">
        <div className="analysis-loading">Loading analysis...</div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="analysis-page">
        <div className="data-alert">{error || "Analysis page is unavailable."}</div>
      </div>
    );
  }

  return (
    <div className="analysis-page">
      <section className="analysis-hero">
        <p className="eyebrow">Analysis</p>
        <h2>{summary.title}</h2>
        <p>{summary.subtitle}</p>
      </section>

      <section className="kpi-grid" aria-label={`${summary.title} KPIs`}>
        {summary.kpis.map((kpi) => (
          <KpiCard key={kpi.label} {...kpi} />
        ))}
      </section>

      <section className="dashboard-grid">
        {summary.sections.map((section) => (
          <SectionRenderer key={`${section.kicker}-${section.title}`} section={section} />
        ))}
      </section>
    </div>
  );
}


export default DeepDivePage;
