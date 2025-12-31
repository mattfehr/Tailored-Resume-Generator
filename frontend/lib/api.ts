import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api", // point to backend
});

// Automatically handle Content-Type for JSON vs FormData
api.interceptors.request.use((config) => {
  const isFormData =
    typeof FormData !== "undefined" && config.data instanceof FormData;

  config.headers = config.headers ?? {};

  if (isFormData) {
    // Let axios set multipart/form-data boundary
    delete (config.headers as any)["Content-Type"];
  } else {
    // Default to JSON for non-FormData payloads
    if (!(config.headers as any)["Content-Type"]) {
      (config.headers as any)["Content-Type"] = "application/json";
    }
  }

  return config;
});

export default api;
