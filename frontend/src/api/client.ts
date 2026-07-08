import axios from "axios";
import { getAccessToken, removeAccessToken } from "../utils/authStorage";

const client = axios.create({
    baseURL: "http://localhost:8000",
    headers: {
        "Content-Type": "application/json",
    },
});

client.interceptors.request.use((config) => {
    const token = getAccessToken();

    if(token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;

    if (status === 401 || status === 403) {
      removeAccessToken();

    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
    }

    return Promise.reject(error);
  }
);

client.interceptors.request.use((config) => {

    const token = localStorage.getItem("access_token");

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

export default client;