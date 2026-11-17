import client from "./client";

export const fetchCart = () => client.get("/cart/").then((r) => r.data);
export const addToCart = (variant, quantity = 1) =>
  client.post("/cart/items/", { variant, quantity }).then((r) => r.data);
export const updateCartItem = (itemId, quantity) =>
  client.patch(`/cart/items/${itemId}/`, { quantity }).then((r) => r.data);
export const removeCartItem = (itemId) => client.delete(`/cart/items/${itemId}/`).then((r) => r.data);
