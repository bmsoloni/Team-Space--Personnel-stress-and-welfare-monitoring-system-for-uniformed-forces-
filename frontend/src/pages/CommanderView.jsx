import { useEffect, useState } from "react";
import { getUnitBreakdownApi } from "../api/dashboardApi";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";
import LoadingSpinner from "../components/common/LoadingSpinner";

export default function CommanderView() {
  const [units, setUnits] = useState([]); const [loading, setLoading] = useState(true);
  useEffect(() => { getUnitBreakdownApi().then(r => { setUnits(r.data); setLoading(false); }).catch(() => setLoading(false)); }, []);
  if (loading) return <LoadingSpinner />;
  return (
    <div>
      <div className="page-header"><div><h1>Unit Overview</h1><div className="breadcrumb">Aggregated unit-level welfare intelligence — no individual identification</div></div></div>
      <div style={{ padding:"12px 16px",background:"rgba(245,158,11,0.08)",border:"1px solid rgba(245,158,11,0.2)",borderRadius:"8px",marginBottom:"20px",fontSize:"13px",color:"var(--accent-yellow)" }}>⚠️ Commander View: This view shows aggregated unit statistics only. Individual personnel data is not displayed here to protect privacy.</div>
      <div className="card" style={{ marginBottom:"20px" }}>
        <h3 style={{ marginBottom:"16px",fontSize:"15px",fontWeight:"600" }}>📊 Risk Distribution by Unit</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={units}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="unit" tick={{ fontSize:11,fill:"var(--text-muted)" }} />
            <YAxis tick={{ fontSize:11,fill:"var(--text-muted)" }} />
            <Tooltip contentStyle={{ background:"var(--bg-card)",border:"1px solid var(--border)",borderRadius:"8px" }} />
            <Legend />
            <Bar dataKey="LOW" stackId="a" fill="#10b981" name="Low" />
            <Bar dataKey="MODERATE" stackId="a" fill="#3b82f6" name="Moderate" />
            <Bar dataKey="HIGH" stackId="a" fill="#f97316" name="High" />
            <Bar dataKey="CRITICAL" stackId="a" fill="#ef4444" name="Critical" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(250px,1fr))",gap:"16px" }}>
        {units.map(u => (
          <div key={u.unit} className="card">
            <div style={{ fontWeight:"700",fontSize:"15px",marginBottom:"12px" }}>{u.unit}</div>
            <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr",gap:"8px",marginBottom:"12px" }}>
              {[["LOW","#10b981"],["MODERATE","#3b82f6"],["HIGH","#f97316"],["CRITICAL","#ef4444"]].map(([r,c]) => (
                <div key={r} style={{ padding:"8px",background:`${c}15`,border:`1px solid ${c}30`,borderRadius:"6px",textAlign:"center" }}>
                  <div style={{ fontSize:"20px",fontWeight:"800",color:c }}>{u[r]}</div>
                  <div style={{ fontSize:"10px",color:"var(--text-muted)" }}>{r}</div>
                </div>
              ))}
            </div>
            <div style={{ display:"flex",justifyContent:"space-between",fontSize:"12px",color:"var(--text-muted)",paddingTop:"8px",borderTop:"1px solid var(--border)" }}>
              <span>Total: <strong style={{ color:"var(--text-primary)" }}>{u.total}</strong></span>
              <span>Avg Stress: <strong style={{ color:"var(--accent-orange)" }}>{u.avg_stress}</strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
