import { createSlice } from "@reduxjs/toolkit";
const personnelSlice = createSlice({
  name: "personnel",
  initialState: { list: [], selected: null, loading: false, error: null },
  reducers: {
    setList(state, { payload }) { state.list = payload; },
    setSelected(state, { payload }) { state.selected = payload; },
    setLoading(state, { payload }) { state.loading = payload; },
    setError(state, { payload }) { state.error = payload; },
  },
});
export const { setList, setSelected, setLoading, setError } = personnelSlice.actions;
export default personnelSlice.reducer;
