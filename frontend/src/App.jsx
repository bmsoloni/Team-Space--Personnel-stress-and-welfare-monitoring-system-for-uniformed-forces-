import { Routes, Route, Navigate } from "react-router-dom";
import { useSelector } from "react-redux";
import ProtectedRoute from "./components/common/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import PersonnelList from "./pages/PersonnelList";
import PersonnelDetail from "./pages/PersonnelDetail";
import Alerts from "./pages/Alerts";
import Reports from "./pages/Reports";
import WelfareChatbotPage from "./pages/WelfareChatbotPage";
import SelfAssessment from "./pages/SelfAssessment";
import CommanderView from "./pages/CommanderView";
import AdminPanel from "./pages/AdminPanel";

export default function App() {
  const { token } = useSelector((s) => s.auth);
  return (
    <Routes>
      <Route path="/login" element={token ? <Navigate to="/" /> : <Login />} />
      <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/personnel" element={<ProtectedRoute roles={["welfare_officer","super_admin"]}><PersonnelList /></ProtectedRoute>} />
      <Route path="/personnel/:id" element={<ProtectedRoute roles={["welfare_officer","super_admin"]}><PersonnelDetail /></ProtectedRoute>} />
      <Route path="/alerts" element={<ProtectedRoute><Alerts /></ProtectedRoute>} />
      <Route path="/reports" element={<ProtectedRoute roles={["welfare_officer","super_admin"]}><Reports /></ProtectedRoute>} />
      <Route path="/chatbot" element={<ProtectedRoute><WelfareChatbotPage /></ProtectedRoute>} />
      <Route path="/self-assessment" element={<ProtectedRoute><SelfAssessment /></ProtectedRoute>} />
      <Route path="/commander" element={<ProtectedRoute roles={["commander","super_admin"]}><CommanderView /></ProtectedRoute>} />
      <Route path="/admin" element={<ProtectedRoute roles={["super_admin"]}><AdminPanel /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
