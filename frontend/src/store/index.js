import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./authSlice";
import personnelReducer from "./personnelSlice";
import alertReducer from "./alertSlice";
export const store = configureStore({ reducer: { auth: authReducer, personnel: personnelReducer, alert: alertReducer } });
