import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";
import Sidebar from "./Sidebar";
import Header from "./Header";

export default function ProtectedRoute({ children, roles }) {
  const { token, user } = useSelector((s) => s.auth);
  if (!token) return <Navigate to="/login" />;
  if (roles && !roles.includes(user?.role)) return <Navigate to="/" />;
  return (
    <div className="top-app-layout">
      <Header />
      <div className="top-layout-content">
        <main className="page-content">{children}</main>
      </div>
    </div>
  );
}
