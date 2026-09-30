import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import {
  getPersonnelApi,
  createPersonnelApi,
  deletePersonnelApi,
} from "../api/personnelApi";
import LoadingSpinner from "../components/common/LoadingSpinner";
import toast from "react-hot-toast";
import {
  Users, Plus, Trash2, ShieldAlert, Activity,
  Search, X, UserCheck, UserX, RefreshCw,
} from "lucide-react";

const ZONES = ["peace", "field", "high_altitude", "insurgency", "counter_terror"];
const RANKS = ["Constable", "Head Constable", "ASI", "SI", "Inspector", "DSP", "SP", "SSP", "DIG", "IG", "ADG", "DGP"];

const EMPTY_FORM = {
  name: "", service_number: "", rank: "", unit_name: "",
  years_of_service: "", deployment_zone: "peace", family_station: false,
};

export default function AdminPanel() {
  const { user } = useSelector((s) => s.auth);
  const [tab, setTab] = useState("officers");
  const [personnel, setPersonnel] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const loadPersonnel = async () => {
    setLoading(true);
    try {
      const res = await getPersonnelApi({ per_page: 200 });
      setPersonnel(res.data.items || []);
    } catch {
      toast.error("Failed to load personnel");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadPersonnel(); }, []);

  const filtered = personnel.filter((p) =>
    !search ||
    p.name?.toLowerCase().includes(search.toLowerCase()) ||
    p.service_number?.toLowerCase().includes(search.toLowerCase()) ||
    p.rank?.toLowerCase().includes(search.toLowerCase())
  );

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((f) => ({ ...f, [name]: type === "checkbox" ? checked : value }));
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!form.name.trim() || !form.service_number.trim()) {
      toast.error("Name and Service Number are required");
      return;
    }
    setSubmitting(true);
    try {
      await createPersonnelApi({
        ...form,
        years_of_service: parseInt(form.years_of_service) || 0,
      });
      toast.success(`Officer "${form.name}" added successfully`);
      setForm(EMPTY_FORM);
      setShowForm(false);
      loadPersonnel();
    } catch (err) {
      toast.error(err?.response?.data?.error || "Failed to add officer");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      const res = await deletePersonnelApi(deleteTarget.id, deleteTarget.hard);
      toast.success(res.data.message);
      setDeleteTarget(null);
      loadPersonnel();
    } catch (err) {
      toast.error(err?.response?.data?.error || "Operation failed");
    }
  };

  const stats = {
    total: personnel.length,
    active: personnel.filter((p) => p.is_active !== false).length,
    inactive: personnel.filter((p) => p.is_active === false).length,
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header" style={{ marginBottom: "24px" }}>
        <div>
          <h1 style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <ShieldAlert size={24} style={{ color: "var(--accent-blue)" }} />
            Admin Panel
          </h1>
          <div className="breadcrumb">System administration · Officer management</div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid-3" style={{ gap: "16px", marginBottom: "24px" }}>
        {[
          { icon: <Users size={18} />, label: "Total Officers", value: stats.total, color: "var(--accent-blue)" },
          { icon: <UserCheck size={18} />, label: "Active", value: stats.active, color: "var(--accent-green)" },
          { icon: <UserX size={18} />, label: "Deactivated", value: stats.inactive, color: "var(--accent-red)" },
        ].map(({ icon, label, value, color }) => (
          <div key={label} className="card" style={{ display: "flex", alignItems: "center", gap: "16px", padding: "16px 20px" }}>
            <div style={{ width: "40px", height: "40px", borderRadius: "10px", background: `${color}22`, display: "flex", alignItems: "center", justifyContent: "center", color, flexShrink: 0 }}>
              {icon}
            </div>
            <div>
              <div style={{ fontSize: "22px", fontWeight: "700" }}>{value}</div>
              <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>{label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Tab Bar */}
      <div style={{ display: "flex", gap: "4px", marginBottom: "20px", borderBottom: "1px solid var(--border)" }}>
        {[
          { key: "officers", label: "Officer Management", icon: <Users size={14} /> },
          { key: "system", label: "System Overview", icon: <Activity size={14} /> },
        ].map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            style={{
              display: "flex", alignItems: "center", gap: "6px",
              padding: "10px 18px", background: "none", border: "none",
              borderBottom: tab === key ? "2px solid var(--accent-blue)" : "2px solid transparent",
              color: tab === key ? "var(--accent-blue)" : "var(--text-secondary)",
              fontWeight: tab === key ? "600" : "500", fontSize: "14px",
              cursor: "pointer", transition: "var(--transition)", marginBottom: "-1px",
            }}
          >
            {icon}{label}
          </button>
        ))}
      </div>

      {/* Officer Management Tab */}
      {tab === "officers" && (
        <div>
          {/* Toolbar */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "12px" }}>
            <div style={{ position: "relative", flex: "1", minWidth: "220px", maxWidth: "340px" }}>
              <Search size={14} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
              <input
                className="form-input"
                style={{ paddingLeft: "34px" }}
                placeholder="Search by name, service #, rank…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div style={{ display: "flex", gap: "8px" }}>
              <button className="btn btn-secondary btn-sm" onClick={loadPersonnel}>
                <RefreshCw size={14} /> Refresh
              </button>
              <button
                className="btn btn-primary btn-sm"
                style={{ background: "var(--accent-blue, #3b82f6)", color: "#fff", border: "none" }}
                onClick={() => setShowForm((v) => !v)}
              >
                <Plus size={14} /> Add Officer
              </button>
            </div>
          </div>

          {/* Add Officer Form */}
          {showForm && (
            <div className="card" style={{ marginBottom: "20px", border: "1px solid rgba(59,130,246,0.35)", background: "rgba(59,130,246,0.06)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
                <h3 style={{ fontSize: "15px", fontWeight: "600", display: "flex", alignItems: "center", gap: "8px" }}>
                  <Plus size={16} style={{ color: "var(--accent-blue)" }} /> Add New Officer
                </h3>
                <button
                  onClick={() => { setShowForm(false); setForm(EMPTY_FORM); }}
                  style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", padding: "4px" }}
                >
                  <X size={18} />
                </button>
              </div>
              <form onSubmit={handleAdd}>
                <div className="grid-2" style={{ gap: "14px", marginBottom: "14px" }}>
                  <div>
                    <label className="form-label">Full Name <span style={{ color: "var(--accent-red)" }}>*</span></label>
                    <input className="form-input" name="name" value={form.name} onChange={handleFormChange} placeholder="e.g. Ramesh Kumar" required />
                  </div>
                  <div>
                    <label className="form-label">Service Number <span style={{ color: "var(--accent-red)" }}>*</span></label>
                    <input className="form-input" name="service_number" value={form.service_number} onChange={handleFormChange} placeholder="e.g. SN-20241001" required />
                  </div>
                  <div>
                    <label className="form-label">Rank</label>
                    <select className="form-select" name="rank" value={form.rank} onChange={handleFormChange}>
                      <option value="">Select Rank</option>
                      {RANKS.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="form-label">Unit Name</label>
                    <input className="form-input" name="unit_name" value={form.unit_name} onChange={handleFormChange} placeholder="e.g. 3rd Battalion" />
                  </div>
                  <div>
                    <label className="form-label">Years of Service</label>
                    <input className="form-input" type="number" name="years_of_service" min="0" max="40" value={form.years_of_service} onChange={handleFormChange} placeholder="e.g. 8" />
                  </div>
                  <div>
                    <label className="form-label">Deployment Zone</label>
                    <select className="form-select" name="deployment_zone" value={form.deployment_zone} onChange={handleFormChange}>
                      {ZONES.map((z) => (
                        <option key={z} value={z}>{z.replace(/_/g, " ").toUpperCase()}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "14px", cursor: "pointer", marginBottom: "20px" }}>
                  <input type="checkbox" name="family_station" checked={form.family_station} onChange={handleFormChange} />
                  Family at station
                </label>
                <div style={{ display: "flex", gap: "10px" }}>
                  <button type="submit" className="btn btn-primary" disabled={submitting}>
                    {submitting ? "Adding…" : "Add Officer"}
                  </button>
                  <button type="button" className="btn btn-secondary" onClick={() => { setShowForm(false); setForm(EMPTY_FORM); }}>
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Officer Table */}
          <div className="card" style={{ padding: 0, overflow: "hidden" }}>
            <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "14px", fontWeight: "600" }}>Officers ({filtered.length})</span>
            </div>
            {loading ? <LoadingSpinner /> : (
              <div style={{ overflowX: "auto" }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Service #</th>
                      <th>Rank</th>
                      <th>Unit</th>
                      <th>Zone</th>
                      <th>Status</th>
                      <th style={{ textAlign: "right" }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((p) => (
                      <tr key={p.id}>
                        <td style={{ fontWeight: "600" }}>{p.name}</td>
                        <td style={{ fontFamily: "monospace", fontSize: "12px", color: "var(--text-muted)" }}>{p.service_number}</td>
                        <td>{p.rank || "—"}</td>
                        <td>{p.unit_name || "—"}</td>
                        <td>
                          <span style={{ fontSize: "12px", textTransform: "capitalize", color: "var(--text-secondary)" }}>
                            {p.deployment_zone?.replace(/_/g, " ")}
                          </span>
                        </td>
                        <td>
                          <span style={{
                            fontSize: "11px", fontWeight: "600", padding: "2px 8px", borderRadius: "20px",
                            background: p.is_active !== false ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)",
                            color: p.is_active !== false ? "var(--accent-green)" : "var(--accent-red)",
                          }}>
                            {p.is_active !== false ? "Active" : "Inactive"}
                          </span>
                        </td>
                        <td>
                          <div style={{ display: "flex", gap: "6px", justifyContent: "flex-end" }}>
                            {p.is_active !== false && (
                              <button
                                className="btn btn-sm"
                                style={{ background: "rgba(239,68,68,0.1)", color: "var(--accent-red)", border: "1px solid rgba(239,68,68,0.25)" }}
                                onClick={() => setDeleteTarget({ id: p.id, name: p.name, hard: false })}
                              >
                                <UserX size={12} /> Deactivate
                              </button>
                            )}
                            <button
                              className="btn btn-sm"
                              style={{ background: "rgba(239,68,68,0.18)", color: "#ff6b6b", border: "1px solid rgba(239,68,68,0.35)" }}
                              onClick={() => setDeleteTarget({ id: p.id, name: p.name, hard: true })}
                            >
                              <Trash2 size={12} /> Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {filtered.length === 0 && (
                      <tr>
                        <td colSpan="7" style={{ textAlign: "center", color: "var(--text-muted)", padding: "40px" }}>
                          No officers found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* System Overview Tab */}
      {tab === "system" && (
        <div className="grid-2" style={{ gap: "20px" }}>
          {[
            ["📋 Audit Logs", "View immutable access and action logs"],
            ["🤖 AI Models", "Model versions and performance metrics"],
            ["🔍 RAG Index", "Knowledge base and vector index status"],
            ["🔑 User Accounts", "System login accounts and roles"],
          ].map(([t, d]) => (
            <div key={t} className="card">
              <h3 style={{ fontSize: "15px", fontWeight: "600", marginBottom: "8px" }}>{t}</h3>
              <p style={{ fontSize: "13px", color: "var(--text-muted)", marginBottom: "16px" }}>{d}</p>
              <button className="btn btn-secondary btn-sm">Open</button>
            </div>
          ))}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteTarget && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.65)", backdropFilter: "blur(4px)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
        }}>
          <div className="card" style={{ width: "100%", maxWidth: "420px", border: "1px solid rgba(239,68,68,0.4)", boxShadow: "0 0 30px rgba(239,68,68,0.25)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
              <div style={{ width: "40px", height: "40px", borderRadius: "10px", background: "rgba(239,68,68,0.15)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--accent-red)", flexShrink: 0 }}>
                <Trash2 size={20} />
              </div>
              <div>
                <h3 style={{ fontSize: "16px", fontWeight: "700" }}>
                  {deleteTarget.hard ? "Permanently Delete" : "Deactivate"} Officer
                </h3>
                <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                  {deleteTarget.hard ? "This action cannot be undone." : "Record will be retained but marked inactive."}
                </p>
              </div>
            </div>
            <p style={{ fontSize: "14px", marginBottom: "24px", color: "var(--text-secondary)" }}>
              {deleteTarget.hard
                ? <span>Permanently delete <strong style={{ color: "var(--text-primary)" }}>{deleteTarget.name}</strong> and all associated records?</span>
                : <span>Deactivate officer <strong style={{ color: "var(--text-primary)" }}>{deleteTarget.name}</strong>? They will no longer appear in active lists.</span>
              }
            </p>
            <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
              <button className="btn btn-secondary" onClick={() => setDeleteTarget(null)}>Cancel</button>
              <button
                className="btn"
                style={{ background: "var(--accent-red, #ef4444)", color: "#fff", border: "none" }}
                onClick={handleDelete}
              >
                {deleteTarget.hard ? "Delete Permanently" : "Deactivate"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
