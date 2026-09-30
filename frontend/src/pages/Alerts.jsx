import { useEffect, useState } from "react";
import { getAlertsApi, acknowledgeAlertApi, resolveAlertApi, escalateAlertApi } from "../api/alertsApi";
import { useDispatch } from "react-redux";
import { setAlerts, updateAlert } from "../store/alertSlice";
import RiskBadge from "../components/common/RiskBadge";
import LoadingSpinner from "../components/common/LoadingSpinner";
import toast from "react-hot-toast";

const statusColor = { OPEN:"var(--accent-red)", ACKNOWLEDGED:"var(--accent-yellow)", RESOLVED:"var(--accent-green)", ESCALATED:"var(--accent-orange)" };

export default function Alerts() {
  const [alerts, setAlertsState] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const dispatch = useDispatch();

  const load = async () => {
    try {
      const res = await getAlertsApi(filter ? { status: filter } : {});
      setAlertsState(res.data); dispatch(setAlerts(res.data));
    } catch { toast.error("Failed to load alerts"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [filter]);

  const act = async (fn, id, note = null) => {
    try {
      const res = await fn(id, note ? { notes: note } : undefined);
      dispatch(updateAlert(res.data.alert));
      load(); toast.success("Alert updated");
    } catch { toast.error("Action failed"); }
  };

  return (
    <div>
      <div className="page-header">
        <div><h1>Welfare Alerts</h1><div className="breadcrumb">Monitor and manage welfare alerts</div></div>
      </div>
      <div style={{ display:"flex",gap:"8px",marginBottom:"20px",flexWrap:"wrap" }}>
        {["","OPEN","ACKNOWLEDGED","RESOLVED","ESCALATED"].map(s => (
          <button key={s} className={`btn ${filter===s?"btn-primary":"btn-secondary"} btn-sm`} onClick={() => setFilter(s)}>
            {s || "All"}
          </button>
        ))}
      </div>
      {loading ? <LoadingSpinner /> : (
        <div>
          {alerts.length === 0 && <div className="card text-muted" style={{ textAlign:"center",padding:"40px" }}>No alerts found</div>}
          {alerts.map(alert => (
            <div key={alert.id} className={`alert-item severity-${alert.severity}`}>
              <div className="alert-dot" />
              <div style={{ flex:1 }}>
                <div style={{ display:"flex",alignItems:"center",gap:"12px",marginBottom:"6px" }}>
                  <span style={{ fontWeight:"700",fontSize:"14px" }}>{alert.alert_type.replace("_"," ")}</span>
                  <span className={`risk-badge`} style={{ background:`${statusColor[alert.status]}22`,color:statusColor[alert.status],border:`1px solid ${statusColor[alert.status]}44` }}>{alert.status}</span>
                  <span style={{ fontSize:"11px",color:"var(--text-muted)" }}>Personnel #{alert.personnel_id}</span>
                </div>
                <div style={{ fontSize:"12px",color:"var(--text-muted)" }}>Created: {new Date(alert.created_at).toLocaleString("en-IN")}</div>
                {alert.notes && <div style={{ fontSize:"13px",color:"var(--text-secondary)",marginTop:"6px",padding:"8px",background:"var(--bg-secondary)",borderRadius:"6px" }}>{alert.notes}</div>}
              </div>
              {alert.status === "OPEN" && (
                <div style={{ display:"flex",gap:"8px",flexShrink:0 }}>
                  <button className="btn btn-success btn-sm" onClick={() => act(acknowledgeAlertApi, alert.id)}>Acknowledge</button>
                  <button className="btn btn-secondary btn-sm" onClick={() => { const n = prompt("Resolution notes:"); if(n) act(resolveAlertApi, alert.id, n); }}>Resolve</button>
                  <button className="btn btn-danger btn-sm" onClick={() => act(escalateAlertApi, alert.id)}>Escalate</button>
                </div>
              )}
              {alert.status === "ACKNOWLEDGED" && (
                <button className="btn btn-success btn-sm" onClick={() => { const n = prompt("Resolution notes:"); if(n) act(resolveAlertApi, alert.id, n); }}>Resolve</button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
