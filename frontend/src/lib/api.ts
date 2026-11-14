import axios from "axios";

const rawUrl = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api").trim().replace(/\/+$/, "");
const baseURL = rawUrl.endsWith("/api") ? rawUrl : `${rawUrl}/api`;

const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 90000,
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
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("cognify_token");
      localStorage.removeItem("cognify_user");
      if (window.location.pathname !== "/login" && window.location.pathname !== "/" && window.location.pathname !== "/register") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
