import axios from "axios";

const configuredBaseUrl = import.meta.env.VITE_API_URL?.trim();
const devBaseUrl =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8000/api`
    : "http://localhost:8000/api";
const BASE_URL = configuredBaseUrl || (import.meta.env.DEV ? devBaseUrl : "");

if (!BASE_URL) {
  throw new Error("VITE_API_URL is required for production builds.");
}

const client = axios.create({ baseURL: BASE_URL });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("tc_access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Share a single refresh request across concurrent 401 responses.
let refreshPromise = null;

function refreshAccessToken() {
  if (refreshPromise) return refreshPromise;

  const refresh = localStorage.getItem("tc_refresh");
  if (!refresh) return Promise.reject(new Error("No refresh token."));

  refreshPromise = axios
    .post(`${BASE_URL}/auth/login/refresh/`, { refresh })
    .then(({ data }) => {
      localStorage.setItem("tc_access", data.access);
      if (data.refresh) localStorage.setItem("tc_refresh", data.refresh);
      return data.access;
    })
    .catch((refreshError) => {
      localStorage.removeItem("tc_access");
      localStorage.removeItem("tc_refresh");
      window.dispatchEvent(new Event("tc:logout"));
      throw refreshError;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const isAuthAttempt = ["/auth/login/", "/auth/register/"].some((path) =>
      original?.url?.includes(path)
    );

    if (
      error.response?.status === 401 &&
      original &&
      !original._retried &&
      !isAuthAttempt
    ) {
      original._retried = true;
      try {
        const access = await refreshAccessToken();
        original.headers = original.headers || {};
        original.headers.Authorization = `Bearer ${access}`;
        return client(original);
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default client;
