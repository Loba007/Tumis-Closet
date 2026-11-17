import client from "./client";

export const register = (payload) => client.post("/auth/register/", payload).then((r) => r.data);
export const login = (payload) => client.post("/auth/login/", payload).then((r) => r.data);
export const logout = (refresh) => client.post("/auth/logout/", { refresh }).then((r) => r.data);
export const requestPasswordReset = (email) =>
  client.post("/auth/password-reset/", { email }).then((r) => r.data);
export const confirmPasswordReset = (payload) =>
  client.post("/auth/password-reset/confirm/", payload).then((r) => r.data);
export const verifyEmail = (payload) =>
  client.post("/auth/email/verify/", payload).then((r) => r.data);
export const resendEmailVerification = () =>
  client.post("/auth/email/resend/").then((r) => r.data);
export const fetchMe = () => client.get("/auth/me/").then((r) => r.data);
export const updateMe = (payload) => client.patch("/auth/me/", payload).then((r) => r.data);
export const listAddresses = () => client.get("/auth/addresses/").then((r) => r.data);
export const createAddress = (payload) => client.post("/auth/addresses/", payload).then((r) => r.data);
export const updateAddress = (id, payload) =>
  client.patch(`/auth/addresses/${id}/`, payload).then((r) => r.data);
export const deleteAddress = (id) => client.delete(`/auth/addresses/${id}/`).then((r) => r.data);
