import client from "./client";

export const fetchWishlist = () => client.get("/wishlist/").then((r) => r.data);
export const addToWishlist = (product) => client.post("/wishlist/", { product }).then((r) => r.data);
export const removeFromWishlist = (product) =>
  client.delete("/wishlist/", { data: { product } }).then((r) => r.data);
