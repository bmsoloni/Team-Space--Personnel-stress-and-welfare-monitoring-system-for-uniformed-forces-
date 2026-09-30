import api from "./axiosInstance";
export const getAllScoresApi = (params) => api.get("/risk/scores", { params });
export const getRiskByIdApi = (id) => api.get(`/risk/${id}`);
export const getRiskHistoryApi = (id, days = 90) => api.get(`/risk/${id}/history`, { params: { days } });
export const triggerAnalysisApi = (id) => api.post(`/risk/trigger/${id}`);
export const getHeatmapApi = () => api.get("/risk/heatmap");
export const getExplanationApi = (id) => api.get(`/risk/explain/${id}`);
