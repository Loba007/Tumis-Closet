import client from "./client";

export const listReviews = (productId) =>
  client.get("/reviews/", { params: { product: productId } }).then((r) => {
    const data = r.data;
    return Array.isArray(data) ? data : data?.results ?? [];
  });
export const createReview = (payload) => client.post("/reviews/", payload).then((r) => r.data);
