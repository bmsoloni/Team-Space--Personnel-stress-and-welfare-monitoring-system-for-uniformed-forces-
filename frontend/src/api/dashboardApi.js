import api from "./axiosInstance";
export const getDashboardSummaryApi = () => api.get("/dashboard/summary");
export const getTrendApi = (days = 30) => api.get("/dashboard/trend", { params: { days } });
export const getUnitBreakdownApi = () => api.get("/dashboard/unit-breakdown");
export const getAlertsOverviewApi = () => api.get("/dashboard/alerts-overview");
export const getTopRiskApi = (n = 10) => api.get("/dashboard/top-risk", { params: { n } });
