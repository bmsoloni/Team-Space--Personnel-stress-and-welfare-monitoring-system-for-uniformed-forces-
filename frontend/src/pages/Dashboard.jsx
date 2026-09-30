import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from "recharts";
import { Users, AlertTriangle, TrendingUp, Shield } from "lucide-react";
import { getDashboardSummaryApi, getTrendApi, getTopRiskApi } from "../api/dashboardApi";
import { getAlertsApi } from "../api/alertsApi";
import { setAlerts } from "../store/alertSlice";
import RiskBadge from "../components/common/RiskBadge";
import LoadingSpinner from "../components/common/LoadingSpinner";
import toast from "react-hot-toast";

const RISK_COLORS = { LOW: "#10b981", MODERATE: "#f59e0b", HIGH: "#f97316", CRITICAL: "#ef4444" };

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [topRisk, setTopRisk] = useState([]);
  const [loading, setLoading] = useState(true);
  const dispatch = useDispatch();

  useEffect(() => {
    const load = async () => {
      try {
        const [sRes, tRes, rRes, aRes] = await Promise.all([
          getDashboardSummaryApi(), getTrendApi(30), getTopRiskApi(8), getAlertsApi({ status: "OPEN" })
        ]);
        setSummary(sRes.data); setTrend(tRes.data); setTopRisk(rRes.data);
        dispatch(setAlerts(aRes.data));
      } catch (e) {
        console.error(e);
        toast.error("Session expired — please log in again");
      }
      finally { setLoading(false); }
    };
    load();
  }, [dispatch]);

  if (loading) return <LoadingSpinner />;

  const riskDist = summary ? [
    { name: "Low", value: summary.risk_distribution.LOW, color: "#10b981" },
    { name: "Moderate", value: summary.risk_distribution.MODERATE, color: "#f59e0b" },
    { name: "High", value: summary.risk_distribution.HIGH, color: "#f97316" },
    { name: "Critical", value: summary.risk_distribution.CRITICAL, color: "#ef4444" },
  ] : [];

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Welfare Overview</h1>
          <div className="breadcrumb">Real-time personnel welfare monitoring dashboard</div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card" style={{ "--kpi-color": "var(--accent-blue)" }}>
          <div className="kpi-label">Total Personnel</div>
          <div className="kpi-value">{summary?.total_personnel ?? "—"}</div>
          <div className="kpi-sub">{summary?.assessed_personnel} assessed today</div>
        </div>
        <div className="kpi-card" style={{ "--kpi-color": "#ef4444" }}>
          <div className="kpi-label">High Risk</div>
          <div className="kpi-value" style={{ color: "#ef4444" }}>{summary?.high_risk_count ?? "—"}</div>
          <div className="kpi-sub">Require immediate attention</div>
        </div>
        <div className="kpi-card" style={{ "--kpi-color": "#f59e0b" }}>
          <div className="kpi-label">Open Alerts</div>
          <div className="kpi-value" style={{ color: "#f59e0b" }}>{summary?.open_alerts ?? "—"}</div>
          <div className="kpi-sub">{summary?.urgent_alerts} urgent</div>
        </div>
        <div className="kpi-card" style={{ "--kpi-color": "#10b981" }}>
          <div className="kpi-label">Low Risk</div>
          <div className="kpi-value" style={{ color: "#10b981" }}>{summary?.risk_distribution?.LOW ?? "—"}</div>
          <div className="kpi-sub">Personnel in good standing</div>
        </div>
      </div>

      <div className="grid-2" style={{ gap: "20px", marginBottom: "20px" }}>
        {/* Stress Trend Chart */}
        <div className="card">
          <h3 style={{ marginBottom: "16px", fontSize: "15px", fontWeight: "600" }}>📈 30-Day Stress Trend</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "var(--text-muted)" }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fontSize: 11, fill: "var(--text-muted)" }} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: "8px", color: "var(--text-primary)" }} />
              <Line type="monotone" dataKey="avg_stress" stroke="#ef4444" strokeWidth={2} dot={false} name="Avg Stress" />
              <Line type="monotone" dataKey="avg_burnout" stroke="#f97316" strokeWidth={2} dot={false} name="Avg Burnout" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution */}
        <div className="card">
          <h3 style={{ marginBottom: "16px", fontSize: "15px", fontWeight: "600" }}>🎯 Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={riskDist}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="name" tick={{ fontSize: 12, fill: "var(--text-muted)" }} />
              <YAxis tick={{ fontSize: 11, fill: "var(--text-muted)" }} />
              <Tooltip contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: "8px" }} />
              <Bar dataKey="value" radius={[4,4,0,0]}>
                {riskDist.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Risk Personnel */}
      <div className="card">
        <h3 style={{ marginBottom: "16px", fontSize: "15px", fontWeight: "600" }}>🚨 Highest Risk Personnel</h3>
        {topRisk.length === 0 ? <div className="text-muted text-sm">No high-risk personnel found</div> : (
          <div style={{ overflowX: "auto" }}>
            <table className="data-table">
              <thead><tr>
                <th>Rank</th><th>Unit</th><th>Stress Score</th><th>Burnout Score</th><th>Risk Level</th><th>Zone</th><th>Anomaly</th>
              </tr></thead>
              <tbody>
                {topRisk.map(p => (
                  <tr key={p.id}>
                    <td>{p.rank || "—"}</td>
                    <td>{p.unit_name || "—"}</td>
                    <td>
                      <div style={{ display:"flex",alignItems:"center",gap:"8px" }}>
                        <div style={{ flex:1,height:"6px",background:"var(--bg-secondary)",borderRadius:"3px",overflow:"hidden" }}>
                          <div style={{ width:`${p.stress_score}%`,height:"100%",background:`linear-gradient(90deg, #f59e0b, #ef4444)`,borderRadius:"3px" }} />
                        </div>
                        <span style={{ fontSize:"12px",fontWeight:"600",color:"var(--text-primary)" }}>{p.stress_score?.toFixed(1)}</span>
                      </div>
                    </td>
                    <td><span style={{ fontSize:"13px",fontWeight:"600",color:"var(--accent-orange)" }}>{p.burnout_score?.toFixed(1)}</span></td>
                    <td><RiskBadge level={p.overall_risk} /></td>
                    <td><span style={{ fontSize:"12px",textTransform:"capitalize",color:"var(--text-secondary)" }}>{p.deployment_zone?.replace("_"," ")}</span></td>
                    <td>{p.is_anomaly ? <span style={{ color:"var(--accent-red)",fontSize:"12px" }}>⚠️ Yes</span> : <span style={{ color:"var(--text-muted)",fontSize:"12px" }}>No</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
