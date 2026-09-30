import api from "./axiosInstance";
export const loginApi = (data) => api.post("/auth/login", data);
export const logoutApi = () => api.post("/auth/logout");
export const getMeApi = () => api.get("/auth/me");
export const refreshTokenApi = () => api.post("/auth/refresh");
export const changePasswordApi = (data) => api.post("/auth/change-password", data);
export const registerApi = (data) => api.post("/auth/register", data);
