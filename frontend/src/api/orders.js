import client from "./client";

export const checkout = (payload) => client.post("/orders/checkout/", payload).then((r) => r.data);
export const listOrders = (params = {}) => client.get("/orders/", { params }).then((r) => r.data);
export const getOrder = (id) => client.get(`/orders/${id}/`).then((r) => r.data);
export const cancelOrder = (id) => client.post(`/orders/${id}/cancel/`).then((r) => r.data);
export const getShippingQuote = (payload) =>
  client.post("/orders/shipping-quote/", payload).then((r) => r.data);
export const initializePayment = (orderId) =>
  client.post("/payments/initialize/", { order_id: orderId }).then((r) => r.data);
export const verifyPayment = (reference) =>
  client.post("/payments/verify/", { reference }).then((r) => r.data);
