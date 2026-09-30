import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { logout } from "../../store/authSlice";
import { logoutApi } from "../../api/authApi";
import { 
  LayoutDashboard, Users, Bell, FileText, 
  MessageSquare, Activity, Shield, ClipboardCheck,
  LogOut, Phone, Mail, HelpCircle
} from "lucide-react";

const navItems = [
  { to: "/",                icon: LayoutDashboard, label: "Home",             roles: ["welfare_officer","super_admin","commander","medical_officer","personnel"] },
  { to: "/personnel",       icon: Users,            label: "Personnel",        roles: ["welfare_officer","super_admin"] },
  { to: "/alerts",          icon: Bell,             label: "Alerts",           roles: ["welfare_officer","super_admin","commander"] },
  { to: "/reports",         icon: FileText,         label: "Reports",          roles: ["welfare_officer","super_admin"] },
  { to: "/chatbot",         icon: MessageSquare,    label: "AI Advisor",       roles: ["welfare_officer","super_admin","commander","medical_officer","personnel"] },
  { to: "/commander",       icon: Activity,         label: "Unit Overview",    roles: ["commander","super_admin"] },
  { to: "/self-assessment", icon: ClipboardCheck,   label: "My Wellness",      roles: ["personnel"] },
  { to: "/admin",           icon: Shield,           label: "Admin",            roles: ["super_admin"] },
];

export default function Header() {
  const { user } = useSelector((s) => s.auth);
  const { openCount } = useSelector((s) => s.alert);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [showNotif, setShowNotif] = useState(false);

  const filteredNav = navItems.filter((i) => i.roles.includes(user?.role));

  const handleLogout = async () => {
    try { await logoutApi(); } catch {}
    dispatch(logout());
    navigate("/login");
  };

  return (
    <header className="top-layout-header">
      {/* Top Thin Contact Bar */}
      <div className="top-contact-bar">
        <div className="top-contact-left">
          <span><Mail size={12} /> support@gov.in</span>
          <span><Phone size={12} /> 1800-11-2233</span>
        </div>
        <div className="top-contact-right">
          <span>{user?.full_name} ({user?.role?.replace(/_/g, " ")})</span>
          <div className="contact-divider" />
          <span style={{ cursor: "pointer" }} onClick={handleLogout}><LogOut size={12} /> Sign Out</span>
        </div>
      </div>

      {/* Main Yellow Branding Banner */}
      <div className="top-branding-banner">
        <div className="branding-container">
          <div className="branding-emblem">
            <div style={{ fontSize: "32px" }}>🛡️</div>
          </div>
          <div className="branding-text">
            <h1>PERSONNEL WELLNESS ANALYTICS PORTAL</h1>
            <p>Organizing Authority: <strong>Ministry of Home Affairs, Govt. of India</strong></p>
          </div>
          <div className="branding-emblem-right">
            <div style={{ fontSize: "32px" }}>🇮🇳</div>
          </div>
        </div>
      </div>

      {/* White Navigation Bar */}
      <div className="top-nav-bar">
        <div className="nav-container">
          <div className="nav-brand">
            <strong>PWAP</strong> 2026
          </div>
          <nav className="nav-links">
            {filteredNav.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) => `top-nav-item ${isActive ? "active" : ""}`}
              >
                <Icon size={14} />
                <span>{label}</span>
                {label === "Alerts" && openCount > 0 && (
                  <span className="top-nav-badge">{openCount}</span>
                )}
              </NavLink>
            ))}
            
            {/* System Notifications Dropdown */}
            <div className="top-nav-item" style={{ position: "relative" }} onClick={() => setShowNotif(!showNotif)}>
              <Bell size={14} />
              <span>Notifications</span>
              {showNotif && (
                <div style={{
                  position: "absolute", top: "calc(100% + 10px)", right: 0, width: "320px",
                  background: "#fff", border: "1px solid var(--border)", borderRadius: "8px",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)", zIndex: 50, padding: "12px",
                  display: "flex", flexDirection: "column", gap: "10px", textAlign: "left"
                }}>
                  <div style={{ fontSize: "13px", borderBottom: "1px solid var(--border)", paddingBottom: "8px", fontWeight: "bold", color: "var(--text-primary)" }}>System Notifications</div>
                  <div style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: "1.4" }}>• New wellness guidelines have been updated. Please review the updated policy. <span className="badge-new">NEW</span></div>
                  <div style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: "1.4" }}>• System maintenance scheduled for 15th October 2026.</div>
                  <div style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: "1.4" }}>• Ensure all personnel complete their self-assessment by month end.</div>
                </div>
              )}
            </div>

            <div className="top-nav-item">
              <HelpCircle size={14} />
              <span>Contact</span>
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}
