import { NavLink } from "react-router-dom";
import { useSelector } from "react-redux";
import {
  LayoutDashboard, Users, Bell, FileText,
  MessageSquare, Activity, Shield, ClipboardCheck
} from "lucide-react";

const navItems = [
  { to: "/",                icon: LayoutDashboard, label: "Dashboard",      roles: ["welfare_officer","super_admin","commander","medical_officer","personnel"] },
  { to: "/personnel",       icon: Users,            label: "Personnel",      roles: ["welfare_officer","super_admin"] },
  { to: "/alerts",          icon: Bell,             label: "Welfare Alerts", roles: ["welfare_officer","super_admin","commander"] },
  { to: "/reports",         icon: FileText,          label: "Reports",        roles: ["welfare_officer","super_admin"] },
  { to: "/chatbot",         icon: MessageSquare,    label: "AI Advisor",     roles: ["welfare_officer","super_admin","commander","medical_officer","personnel"] },
  { to: "/commander",       icon: Activity,         label: "Unit Overview",  roles: ["commander","super_admin"] },
  { to: "/self-assessment", icon: ClipboardCheck,   label: "My Wellness",    roles: ["personnel"] },
  { to: "/admin",           icon: Shield,           label: "Admin Panel",    roles: ["super_admin"] },
];

export default function Sidebar() {
  const { user } = useSelector((s) => s.auth);
  const { openCount } = useSelector((s) => s.alert);
  const filtered = navItems.filter((i) => i.roles.includes(user?.role));

  return (
    <aside className="sidebar">
      {/* Top bar — saffron stripe + Ministry label only */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-top">
          <div className="sidebar-logo-text">
            <h2>Personnel Wellness<br />Analytics Portal</h2>
            <p>Ministry of Home Affairs</p>
          </div>
        </div>
        <div className="sidebar-ministry">
          Govt. of India · Confidential
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="sidebar-section">Navigation</div>
        {filtered.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <Icon size={16} strokeWidth={2} />
            <span>{label}</span>
            {label === "Welfare Alerts" && openCount > 0 && (
              <span className="nav-badge">{openCount}</span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User Info */}
      <div className="sidebar-user">
        <div className="sidebar-user-name">{user?.full_name || "—"}</div>
        <div className="sidebar-user-role">{user?.role?.replace(/_/g, " ") || "—"}</div>
      </div>
    </aside>
  );
}
