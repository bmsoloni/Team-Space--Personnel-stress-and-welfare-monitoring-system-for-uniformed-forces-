import { createSlice } from "@reduxjs/toolkit";
const stored = localStorage.getItem("swm_token");
const storedUser = localStorage.getItem("swm_user");
const authSlice = createSlice({
  name: "auth",
  initialState: { token: stored || null, user: storedUser ? JSON.parse(storedUser) : null },
  reducers: {
    setCredentials(state, { payload }) {
      state.token = payload.token;
      state.user = payload.user;
      localStorage.setItem("swm_token", payload.token);
      localStorage.setItem("swm_user", JSON.stringify(payload.user));
    },
    logout(state) {
      state.token = null;
      state.user = null;
      localStorage.removeItem("swm_token");
      localStorage.removeItem("swm_user");
    },
  },
});
export const { setCredentials, logout } = authSlice.actions;
export default authSlice.reducer;
