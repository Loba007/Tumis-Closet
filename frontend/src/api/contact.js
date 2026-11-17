import client from "./client";

export const sendContactMessage = (payload) =>
  client.post("/contact/", payload).then((r) => r.data);
