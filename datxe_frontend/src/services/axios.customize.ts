import axios from "axios";

const instance = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add a request interceptor
instance.interceptors.request.use(
  (config) => {
    // Do something before request is sent
    return config;
  },
  (error) => {
    // Do something with request error
    return Promise.reject(error);
  }
);

// Add a response interceptor
instance.interceptors.response.use(
  (response) => {
    // Do something with response data
    if (response?.data?.data) {
      return response.data;
    }

    return response;
  },
  (error) => {
    // Do something with response error
    if (error?.response?.data) {
      return error.response.data;
    }

    return Promise.reject(error);
  }
);

export default instance;
