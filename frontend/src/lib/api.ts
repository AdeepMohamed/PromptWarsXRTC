import axios from "axios";

const rawUrl = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api").trim().replace(/\/+$/, "");
const baseURL = rawUrl.endsWith("/api") ? rawUrl : `${rawUrl}/api`;

const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 120000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("cognify_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config as any;

    if (error.response?.status === 401) {
      localStorage.removeItem("cognify_token");
      localStorage.removeItem("cognify_user");
      if (window.location.pathname !== "/login" && window.location.pathname !== "/" && window.location.pathname !== "/register") {
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }

    // Resilient auto-retry for Render serverless cold-starts (up to 3 automatic retries)
    if (config) {
      config.retryCount = config.retryCount || 0;
      const isNetworkOrTimeout =
        !error.response ||
        [408, 502, 503, 504].includes(error.response?.status) ||
        error.code === "ECONNABORTED";

      if (isNetworkOrTimeout && config.retryCount < 3) {
        config.retryCount += 1;
        const delay = Math.min(config.retryCount * 2500, 7000);
        await new Promise((resolve) => setTimeout(resolve, delay));
        return api(config);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
