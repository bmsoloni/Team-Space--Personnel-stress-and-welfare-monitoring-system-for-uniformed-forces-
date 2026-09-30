import { createSlice } from "@reduxjs/toolkit";
const alertSlice = createSlice({
  name: "alert",
  initialState: { alerts: [], openCount: 0 },
  reducers: {
    setAlerts(state, { payload }) { state.alerts = payload; state.openCount = payload.filter(a => a.status === "OPEN").length; },
    updateAlert(state, { payload }) { const i = state.alerts.findIndex(a => a.id === payload.id); if (i >= 0) state.alerts[i] = payload; },
  },
});
export const { setAlerts, updateAlert } = alertSlice.actions;
export default alertSlice.reducer;
