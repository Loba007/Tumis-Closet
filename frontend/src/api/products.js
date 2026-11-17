import client from "./client";

export const listProducts = (params = {}) => client.get("/products/", { params }).then((r) => r.data);
export const getProduct = (slug) => client.get(`/products/${slug}/`).then((r) => r.data);
export const listPortfolio = (params = {}) =>
  client.get("/products/", { params: { portfolio: "true", ...params } }).then((r) => r.data);
export const listCategories = () => client.get("/categories/").then((r) => r.data);
