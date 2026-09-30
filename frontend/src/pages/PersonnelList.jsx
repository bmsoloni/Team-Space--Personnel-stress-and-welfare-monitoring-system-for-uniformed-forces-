import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getPersonnelApi } from "../api/personnelApi";
import { triggerAnalysisApi } from "../api/riskApi";
import RiskBadge from "../components/common/RiskBadge";
import LoadingSpinner from "../components/common/LoadingSpinner";
import toast from "react-hot-toast";
import { Search, RefreshCw, Eye } from "lucide-react";

export default function PersonnelList() {
  const [data, setData] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ q: "", zone: "", risk: "" });
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    try { const res = await getPersonnelApi(filters); setData(res.data); }
    catch (e) { toast.error("Failed to load personnel"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [filters]);

  const handleTrigger = async (id, e) => {
    e.stopPropagation();
    toast.loading("Running AI analysis...", { id: "trigger" });
    try {
      await triggerAnalysisApi(id);
      toast.success("Risk analysis complete!", { id: "trigger" });
      load();
    } catch { toast.error("Analysis failed", { id: "trigger" }); }
  };

  return (
    <div>
      <div className="page-header">
        <div><h1>Personnel</h1><div className="breadcrumb">Manage and monitor uniformed personnel</div></div>
      </div>
      <div className="card" style={{ marginBottom: "20px", padding: "16px" }}>
        <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
          <div style={{ flex: 1, minWidth: "200px", position: "relative" }}>
            <Search size={14} style={{ position:"absolute",left:"12px",top:"50%",transform:"translateY(-50%)",color:"var(--text-muted)" }} />
            <input className="form-input" style={{ paddingLeft:"34px" }} placeholder="Search personnel..." value={filters.q} onChange={e => setFilters(f => ({...f, q: e.target.value}))} />
          </div>
          <select className="form-select" style={{ width:"auto" }} value={filters.zone} onChange={e => setFilters(f => ({...f, zone: e.target.value}))}>
            <option value="">All Zones</option>
            {["peace","field","high_altitude","insurgency","counter_terror"].map(z => <option key={z} value={z}>{z.replace("_"," ").toUpperCase()}</option>)}
          </select>
          <select className="form-select" style={{ width:"auto" }} value={filters.risk} onChange={e => setFilters(f => ({...f, risk: e.target.value}))}>
            <option value="">All Risk Levels</option>
            {["LOW","MODERATE","HIGH","CRITICAL"].map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
      </div>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
          <span style={{ fontSize:"14px", fontWeight:"600" }}>Personnel List ({data.total || data.items?.length || 0})</span>
          <button className="btn btn-secondary btn-sm" onClick={load}><RefreshCw size={14} />Refresh</button>
        </div>
        {loading ? <LoadingSpinner /> : (
          <div style={{ overflowX: "auto" }}>
            <table className="data-table">
              <thead><tr><th>Name</th><th>Service #</th><th>Rank</th><th>Unit</th><th>Zone</th><th>Risk Level</th><th>Stress</th><th>Actions</th></tr></thead>
              <tbody>
                {data.items?.map(p => (
                  <tr key={p.id} style={{ cursor:"pointer" }} onClick={() => navigate(`/personnel/${p.id}`)}>
                    <td style={{ fontWeight:"600" }}>{p.name}</td>
                    <td style={{ fontFamily:"monospace",fontSize:"12px",color:"var(--text-muted)" }}>{p.service_number}</td>
                    <td>{p.rank || "—"}</td>
                    <td>{p.unit_name || "—"}</td>
                    <td><span style={{ fontSize:"12px",textTransform:"capitalize",color:"var(--text-secondary)" }}>{p.deployment_zone?.replace("_"," ")}</span></td>
                    <td><RiskBadge level={p.latest_risk} /></td>
                    <td>
                      {p.stress_score != null ? (
                        <div style={{ display:"flex",alignItems:"center",gap:"6px",minWidth:"100px" }}>
                          <div style={{ flex:1,height:"5px",background:"var(--bg-secondary)",borderRadius:"3px",overflow:"hidden" }}>
                            <div style={{ width:`${p.stress_score}%`,height:"100%",background:"linear-gradient(90deg,#f59e0b,#ef4444)" }} />
                          </div>
                          <span style={{ fontSize:"11px" }}>{p.stress_score?.toFixed(0)}</span>
                        </div>
                      ) : <span className="text-muted text-xs">N/A</span>}
                    </td>
                    <td style={{ display:"flex",gap:"8px" }}>
                      <button className="btn btn-secondary btn-sm" onClick={e => { e.stopPropagation(); navigate(`/personnel/${p.id}`); }}><Eye size={12} />View</button>
                      <button className="btn btn-sm" style={{ background:"rgba(59,130,246,0.1)",color:"var(--accent-blue)",border:"1px solid rgba(59,130,246,0.2)" }} onClick={e => handleTrigger(p.id, e)}><RefreshCw size={12} />Analyze</button>
                    </td>
                  </tr>
                ))}
                {data.items?.length === 0 && <tr><td colSpan="8" style={{ textAlign:"center",color:"var(--text-muted)",padding:"40px" }}>No personnel found</td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
