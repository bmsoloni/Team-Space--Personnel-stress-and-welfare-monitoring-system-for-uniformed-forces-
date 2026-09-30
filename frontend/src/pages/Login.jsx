import { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { loginApi, registerApi } from "../api/authApi";
import { setCredentials } from "../store/authSlice";
import { Lock, Mail, User } from "lucide-react";

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let res;
      if (isLogin) {
        res = await loginApi({ email: form.email, password: form.password });
        toast.success(`Welcome, ${res.data.user.full_name}`);
      } else {
        res = await registerApi(form);
        toast.success(`Registration successful. Welcome, ${res.data.user.full_name}`);
      }
      
      dispatch(setCredentials({ token: res.data.access_token, user: res.data.user }));
      localStorage.setItem("swm_refresh", res.data.refresh_token);
      navigate("/");
    } catch (err) {
      toast.error(err.response?.data?.error || (isLogin ? "Login failed. Please check your credentials." : "Registration failed."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card-container">
        
        {/* Header / Branding */}
        <div className="login-header-text">
          <div style={{ display: "flex", gap: "6px", justifyContent: "center", marginBottom: "12px" }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--gov-saffron)" }} />
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#cccccc" }} />
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--gov-green)" }} />
          </div>
          <h1>Personnel Wellness Analytics Portal</h1>
          <p>Ministry of Home Affairs | Govt. of India</p>
        </div>

        <div className="login-card-header">
          <h2>{isLogin ? "Secure Sign In" : "Official Registration"}</h2>
          <p>{isLogin ? "Enter your credentials to access the system" : "Register for an official portal account"}</p>
        </div>

        {/* Toggle Tabs */}
        <div style={{ display: "flex", marginBottom: "24px", borderBottom: "2px solid var(--border)", gap: "20px", justifyContent: "center" }}>
          <div 
            onClick={() => setIsLogin(true)} 
            style={{
              paddingBottom: "8px", 
              cursor: "pointer", 
              fontWeight: 700, 
              fontSize: "12px",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              color: isLogin ? "var(--gov-navy)" : "var(--text-muted)",
              borderBottom: isLogin ? "3px solid var(--gov-saffron)" : "3px solid transparent",
              transition: "all 0.2s"
            }}>
            Sign In
          </div>
          <div 
            onClick={() => setIsLogin(false)} 
            style={{
              paddingBottom: "8px", 
              cursor: "pointer", 
              fontWeight: 700, 
              fontSize: "12px",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              color: !isLogin ? "var(--gov-navy)" : "var(--text-muted)",
              borderBottom: !isLogin ? "3px solid var(--gov-saffron)" : "3px solid transparent",
              transition: "all 0.2s"
            }}>
            Register
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <div style={{ position: "relative" }}>
                <User size={14} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
                <input
                  className="form-input"
                  type="text"
                  placeholder="Inspector Rajesh Kumar"
                  style={{ paddingLeft: "34px" }}
                  value={form.full_name}
                  onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
                  required={!isLogin}
                />
              </div>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Official Email Address</label>
            <div style={{ position: "relative" }}>
              <Mail size={14} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
              <input
                className="form-input"
                type="email"
                placeholder="officer@gov.in"
                style={{ paddingLeft: "34px" }}
                value={form.email}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={{ position: "relative" }}>
              <Lock size={14} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
              <input
                className="form-input"
                type="password"
                placeholder="••••••••"
                style={{ paddingLeft: "34px" }}
                value={form.password}
                onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                required
              />
            </div>
          </div>

          <button
            className="btn btn-primary w-full"
            type="submit"
            style={{ justifyContent: "center", marginTop: "12px", padding: "11px 18px", fontSize: "13px" }}
            disabled={loading}
          >
            {loading ? "Processing..." : (isLogin ? "Sign In Securely" : "Register Securely")}
          </button>
        </form>

        <div style={{
          marginTop: "24px",
          paddingTop: "16px",
          borderTop: "1px solid var(--border)",
          fontSize: "10px",
          color: "var(--text-muted)",
          textAlign: "center",
          lineHeight: 1.6,
        }}>
          By proceeding, you agree to the Official Secrets Act &amp; IT Act obligations.<br />
          Unauthorized access is a punishable offence.
        </div>
      </div>
    </div>
  );
}
