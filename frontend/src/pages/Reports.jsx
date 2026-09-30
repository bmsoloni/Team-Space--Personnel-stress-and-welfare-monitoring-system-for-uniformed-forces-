import { useState } from "react";
import { generateReportApi, downloadReportApi } from "../api/reportsApi";
import toast from "react-hot-toast";
import { FileText, Download } from "lucide-react";

export default function Reports() {
  const [form, setForm] = useState({ type: "unit_summary", format: "pdf" });
  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState(null);

  const generate = async () => {
    setLoading(true);
    toast.loading("Generating report...", { id: "gen" });
    try {
      const res = await generateReportApi(form);
      setGenerated(res.data);
      toast.success("Report generated!", { id: "gen" });
    } catch { toast.error("Failed to generate report", { id: "gen" }); }
    finally { setLoading(false); }
  };

  const download = async () => {
    try {
      const res = await downloadReportApi(generated.report_id);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a"); a.href = url; a.download = generated.filename; a.click();
    } catch { toast.error("Download failed"); }
  };

  return (
    <div>
      <div className="page-header"><div><h1>Reports</h1><div className="breadcrumb">Generate welfare and risk reports</div></div></div>
      <div className="grid-2" style={{ gap:"20px" }}>
        <div className="card">
          <h3 style={{ marginBottom:"20px",fontSize:"15px",fontWeight:"600" }}>📋 Generate Report</h3>
          <div className="form-group">
            <label className="form-label">Report Type</label>
            <select className="form-select" value={form.type} onChange={e => setForm(f => ({...f, type: e.target.value}))}>
              <option value="unit_summary">Unit Summary</option>
              <option value="high_risk">High Risk Personnel</option>
              <option value="alerts_summary">Alerts Summary</option>
              <option value="wellness_trends">Wellness Trends</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Format</label>
            <div style={{ display:"flex",gap:"12px" }}>
              {["pdf","excel"].map(f => (
                <label key={f} style={{ display:"flex",alignItems:"center",gap:"8px",cursor:"pointer" }}>
                  <input type="radio" name="format" value={f} checked={form.format===f} onChange={e => setForm(fv => ({...fv, format: e.target.value}))} />
                  <span style={{ textTransform:"uppercase",fontWeight:"600",fontSize:"13px" }}>{f}</span>
                </label>
              ))}
            </div>
          </div>
          <button className="btn btn-primary" onClick={generate} disabled={loading} style={{ width:"100%",justifyContent:"center" }}>
            <FileText size={16} />{loading ? "Generating..." : "Generate Report"}
          </button>
          {generated && (
            <div style={{ marginTop:"16px",padding:"16px",background:"rgba(16,185,129,0.08)",border:"1px solid rgba(16,185,129,0.2)",borderRadius:"8px" }}>
              <div style={{ fontSize:"13px",fontWeight:"600",color:"var(--accent-green)",marginBottom:"8px" }}>✅ Report Ready: {generated.filename}</div>
              <button className="btn btn-success btn-sm" onClick={download}><Download size={14} />Download {generated.format.toUpperCase()}</button>
            </div>
          )}
        </div>
        <div className="card">
          <h3 style={{ marginBottom:"16px",fontSize:"15px",fontWeight:"600" }}>ℹ️ Report Types</h3>
          {[["Unit Summary","Overview of risk distribution across all units"],["High Risk Personnel","Detailed list of HIGH and CRITICAL risk personnel"],["Alerts Summary","Status and resolution breakdown of all alerts"],["Wellness Trends","Aggregated wellness assessment trends over time"]].map(([t,d]) => (
            <div key={t} style={{ padding:"12px",borderRadius:"8px",background:"var(--bg-secondary)",border:"1px solid var(--border)",marginBottom:"8px" }}>
              <div style={{ fontWeight:"600",fontSize:"13px",marginBottom:"4px" }}>{t}</div>
              <div style={{ fontSize:"12px",color:"var(--text-muted)" }}>{d}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
