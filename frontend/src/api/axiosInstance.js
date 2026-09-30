import axios from "axios";
import { store } from "../store";
import { logout, setCredentials } from "../store/authSlice";

const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || "/api", timeout: 120000 });

api.interceptors.request.use((config) => {
  const token = store.getState().auth.token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;
    // Only attempt refresh once, and never on the refresh call itself
    if (err.response?.status === 401 && !original._retry && !original.url?.includes("/auth/refresh")) {
      original._retry = true;
      try {
        const refreshToken = localStorage.getItem("swm_refresh");
        if (!refreshToken) throw new Error("No refresh token");
        const baseURL = import.meta.env.VITE_API_BASE_URL || "/api";
        const res = await axios.post(`${baseURL}/auth/refresh`, {}, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        });
        const newToken = res.data.access_token;
        store.dispatch(setCredentials({ token: newToken, user: store.getState().auth.user }));
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      } catch {
        // Refresh failed — clear everything and go to login
        localStorage.removeItem("swm_refresh");
        store.dispatch(logout());
        window.location.href = "/login";
        return Promise.reject(new Error("Session expired"));
      }
    }
    return Promise.reject(err);
  }
);

export default api;
