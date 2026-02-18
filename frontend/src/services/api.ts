import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';

// API base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds (podcast generation can take time)
});

// Request interceptor — attach JWT token if present
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle errors globally
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as Record<string, unknown>;
      const message =
        (data?.detail as string) ||
        (data?.message as string) ||
        error.message ||
        'Произошла ошибка';

      if (status === 401) {
        // Token expired or invalid — clear storage and redirect to login
        localStorage.removeItem('access_token');
        // Only show toast if not already on login page
        if (!window.location.pathname.includes('/login')) {
          toast.error('Сессия истекла. Пожалуйста, войдите снова.');
        }
      } else if (status === 403) {
        toast.error('Доступ запрещён');
      } else if (status === 429) {
        toast.error('Слишком много запросов. Подождите немного.');
      } else if (status >= 500) {
        toast.error('Ошибка сервера. Попробуйте позже.');
      } else {
        toast.error(message);
      }
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Превышено время ожидания запроса');
    } else if (!error.response) {
      toast.error('Нет соединения с сервером');
    }

    return Promise.reject(error);
  }
);

export default apiClient;
