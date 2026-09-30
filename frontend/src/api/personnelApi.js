import api from "./axiosInstance";
export const getPersonnelApi = (params) => api.get("/personnel/", { params });
export const getPersonnelByIdApi = (id) => api.get(`/personnel/${id}`);
export const getRiskTimelineApi = (id, days = 90) => api.get(`/personnel/${id}/risk-timeline`, { params: { days } });
export const getLeavesApi = (id) => api.get(`/personnel/${id}/leaves`);
export const getDeploymentsApi = (id) => api.get(`/personnel/${id}/deployments`);
export const createPersonnelApi = (data) => api.post("/personnel/", data);
export const updatePersonnelApi = (id, data) => api.put(`/personnel/${id}`, data);
export const deletePersonnelApi = (id, hard = false) => api.delete(`/personnel/${id}`, { params: { hard } });
