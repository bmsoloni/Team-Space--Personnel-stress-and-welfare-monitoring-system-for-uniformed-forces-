import api from "./axiosInstance";
export const generateReportApi = (data) => api.post("/reports/generate", data);
export const listReportsApi = () => api.get("/reports/");
export const downloadReportApi = (id) => api.get(`/reports/${id}/download`, { responseType: "blob" });
