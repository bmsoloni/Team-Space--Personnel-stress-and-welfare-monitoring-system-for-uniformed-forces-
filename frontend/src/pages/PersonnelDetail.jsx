import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { getPersonnelByIdApi, getRiskTimelineApi, getLeavesApi } from "../api/personnelApi";
import { getRecommendationApi, explainScoreApi } from "../api/ragApi";
import RiskBadge from "../components/common/RiskBadge";
import LoadingSpinner from "../components/common/LoadingSpinner";
import toast from "react-hot-toast";
import { ArrowLeft, Brain, Zap } from "lucide-react";

export default function PersonnelDetail() {
  const { id } = useParams(); const navigate = useNavigate();
  const [person, setPerson] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [leaves, setLeaves] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [pRes, tRes, lRes] = await Promise.all([getPersonnelByIdApi(id), getRiskTimelineApi(id), getLeavesApi(id)]);
        setPerson(pRes.data); setTimeline(tRes.data); setLeaves(lRes.data);
      } catch { toast.error("Failed to load personnel data"); }
      finally { setLoading(false); }
    };
    load();
  }, [id]);

  const handleRecommend = async () => {
    toast.loading("Generating AI recommendation...", { id: "rec" });
    try { const res = await getRecommendationApi(id); setRecommendation(res.data); toast.success("Recommendation ready", { id: "rec" }); }
    catch { toast.error("Failed to get recommendation", { id: "rec" }); }
  };

  const handleExplain = async () => {
    toast.loading("Generating AI explanation...", { id: "exp" });
    try { const res = await explainScoreApi(id); setExplanation(res.data); toast.success("Explanation ready", { id: "exp" }); }
    catch { toast.error("Failed to explain score", { id: "exp" }); }
  };

  if (loading) return <LoadingSpinner />;
  if (!person) return <div className="text-muted">Person not found</div>;
  const risk = person.latest_risk_score;
  const factors = risk?.risk_factors?.top_factors || [];

  return (
    <div>
      <div className="page-header">
        <div style={{ display:"flex",alignItems:"center",gap:"12px" }}>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate("/personnel")}><ArrowLeft size={14} />Back</button>
          <div><h1>{person.name}</h1><div className="breadcrumb">{person.rank} · {person.unit_name} · {person.deployment_zone?.replace("_"," ").toUpperCase()}</div></div>
        </div>
        <div style={{ display:"flex",gap:"10px" }}>
          <button className="btn btn-secondary" onClick={handleExplain}><Brain size={16} />AI Explain</button>
          <button className="btn btn-primary" onClick={handleRecommend}><Zap size={16} />Get Recommendation</button>
        </div>
      </div>
      <div className="grid-2" style={{ gap:"20px", marginBottom:"20px" }}>
        <div className="card">
          <h3 style={{ marginBottom:"16px",fontSize:"15px",fontWeight:"600" }}>👤 Profile</h3>
          <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr",gap:"12px" }}>
            {[["Service Number", person.service_number],["Rank", person.rank],["Unit", person.unit_name],["Years of Service", person.years_of_service],["Deployment Zone", person.deployment_zone?.replace("_"," ")],["Family Station", person.family_station ? "Yes":"No"]].map(([k,v]) => (
              <div key={k}><div className="text-xs text-muted" style={{ marginBottom:"2px" }}>{k}</div><div style={{ fontSize:"14px",fontWeight:"500" }}>{v || "—"}</div></div>
            ))}
          </div>
        </div>
        <div className="card">
          <h3 style={{ marginBottom:"16px",fontSize:"15px",fontWeight:"600" }}>🎯 Current Risk Assessment</h3>
          {risk ? <>
            <div style={{ display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"16px" }}>
              <RiskBadge level={risk.overall_risk} />
              <span style={{ fontSize:"11px",color:"var(--text-muted)" }}>{risk.score_date}</span>
            </div>
            {[["Stress Score", risk.stress_score, "#ef4444"],["Burnout Score", risk.burnout_score, "#f97316"]].map(([label,val,color]) => (
              <div key={label} className="score-bar-wrap">
                <div className="score-bar-label"><span>{label}</span><span style={{ color,fontWeight:"700" }}>{val?.toFixed(1)}</span></div>
                <div className="score-bar"><div className="score-bar-fill" style={{ width:`${val}%`,background:color }} /></div>
              </div>
            ))}
            {risk.is_anomaly && <div style={{ marginTop:"12px",padding:"8px 12px",background:"rgba(239,68,68,0.1)",border:"1px solid rgba(239,68,68,0.2)",borderRadius:"6px",fontSize:"12px",color:"var(--accent-red)" }}>⚠️ Anomalous behavior pattern detected</div>}
          </> : <div className="text-muted">No risk assessment available</div>}
        </div>
      </div>

      {/* Risk Factors */}
      {factors.length > 0 && (
        <div className="card" style={{ marginBottom:"20px" }}>
          <h3 style={{ marginBottom:"16px",fontSize:"15px",fontWeight:"600" }}>🔬 Key Risk Factors</h3>
          <div style={{ display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(200px,1fr))",gap:"12px" }}>
            {factors.map((f,i) => (
              <div key={i} style={{ padding:"12px",background:"var(--bg-secondary)",borderRadius:"8px",border:`1px solid ${f.direction==="increases_risk"?"rgba(239,68,68,0.2)":"rgba(16,185,129,0.2)"}` }}>
                <div style={{ fontSize:"11px",color:"var(--text-muted)",marginBottom:"4px" }}>{f.factor.replace(/_/g," ").toUpperCase()}</div>
                <div style={{ fontSize:"18px",fontWeight:"700",color:f.direction==="increases_risk"?"var(--accent-red)":"var(--accent-green)" }}>{f.value}</div>
                <div style={{ fontSize:"11px",marginTop:"4px",color:f.direction==="increases_risk"?"#f97316":"#10b981" }}>
                  {f.direction==="increases_risk"?"↑":"↓"} {Math.abs(f.contribution).toFixed(1)} pts
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risk Timeline */}
      {timeline.length > 0 && (
        <div className="card" style={{ marginBottom:"20px" }}>
          <h3 style={{ marginBottom:"16px",fontSize:"15px",fontWeight:"600" }}>📈 Risk History (90 days)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={timeline}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="score_date" tick={{ fontSize:10,fill:"var(--text-muted)" }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fontSize:10,fill:"var(--text-muted)" }} domain={[0,100]} />
              <Tooltip contentStyle={{ background:"var(--bg-card)",border:"1px solid var(--border)",borderRadius:"8px" }} />
              <Line type="monotone" dataKey="stress_score" stroke="#ef4444" strokeWidth={2} dot={false} name="Stress" />
              <Line type="monotone" dataKey="burnout_score" stroke="#f97316" strokeWidth={2} dot={false} name="Burnout" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* AI Recommendation */}
      {recommendation && (
        <div className="card" style={{ marginBottom:"20px",border:"1px solid rgba(59,130,246,0.3)" }}>
          <h3 style={{ marginBottom:"12px",fontSize:"15px",fontWeight:"600",color:"var(--accent-blue)" }}>🤖 AI Welfare Recommendation</h3>
          <p style={{ fontSize:"14px",lineHeight:"1.8",color:"var(--text-secondary)" }}>{recommendation.answer}</p>
          {recommendation.sources?.length > 0 && (
            <div style={{ marginTop:"12px" }}>
              <div className="text-xs text-muted" style={{ marginBottom:"6px" }}>Sources:</div>
              {recommendation.sources.map((s,i) => <span key={i} className="source-chip">📄 {s.document} p.{s.page}</span>)}
            </div>
          )}
        </div>
      )}

      {/* AI Explanation */}
      {explanation && (
        <div className="card" style={{ border:"1px solid rgba(6,182,212,0.3)" }}>
          <h3 style={{ marginBottom:"12px",fontSize:"15px",fontWeight:"600",color:"var(--accent-cyan)" }}>🧠 AI Explanation of Risk Factors</h3>
          <p style={{ fontSize:"14px",lineHeight:"1.8",color:"var(--text-secondary)" }}>{explanation.answer}</p>
        </div>
      )}
    </div>
  );
}
