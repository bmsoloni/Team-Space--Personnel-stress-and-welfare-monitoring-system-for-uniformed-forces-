import api from "./axiosInstance";
export const chatApi = (data) => api.post("/rag/chat", data);
export const getRecommendationApi = (personnelId) => api.post(`/rag/recommend/${personnelId}`);
export const getSimilarCasesApi = (personnelId) => api.get(`/rag/similar-cases/${personnelId}`);
export const explainScoreApi = (personnelId) => api.post(`/rag/explain-score/${personnelId}`);
export const companionChatApi = (data) => api.post("/rag/companion", data);
export const getRagHistoryApi = () => api.get("/rag/history");
