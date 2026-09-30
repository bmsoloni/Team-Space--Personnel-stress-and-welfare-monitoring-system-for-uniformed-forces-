import api from "./axiosInstance";
export const getAlertsApi = (params) => api.get("/alerts/", { params });
export const getAlertByIdApi = (id) => api.get(`/alerts/${id}`);
export const acknowledgeAlertApi = (id) => api.patch(`/alerts/${id}/acknowledge`);
export const resolveAlertApi = (id, data) => api.patch(`/alerts/${id}/resolve`, data);
export const escalateAlertApi = (id) => api.post(`/alerts/${id}/escalate`);
export const createManualAlertApi = (data) => api.post("/alerts/manual", data);
