import api from "./axiosInstance";
export const getQuestionsApi = () => api.get("/wellness/questions");
export const submitWellnessApi = (data) => api.post("/wellness/submit", data);
export const getWellnessHistoryApi = (id) => api.get(`/wellness/history/${id}`);
export const getWellnessSummaryApi = () => api.get("/wellness/summary");
