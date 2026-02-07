import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface ChatRequest {
  query: string;
  n_results?: number;
  temperature?: number;
  max_tokens?: number;
}

export interface ChatResponse {
  count: number;
  sample_documents: string[];
}

export const chatService = {
  // Send chat message
  async sendMessage(chatRequest: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await apiClient.post('/api/utils/rag/chat', chatRequest);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Handle API errors
  handleError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      // Axios error
      if (error.response) {
        // Server responded with error status
        const message = error.response.data?.message || 'خطا در سرور رخ داد';
        return new Error(message);
      } else if (error.request) {
        // Request was made but no response received
        return new Error('خطا در شبکه. لطفاً اتصال خود را بررسی کنید.');
      } else {
        // Something else happened in setting up the request
        return new Error(error.message || 'خطای غیرمنتظره رخ داد');
      }
    } else if (error instanceof Error) {
      // Generic JavaScript error
      return error;
    } else {
      // Unknown error type
      return new Error('خطای غیرمنتظره رخ داد');
    }
  },
};

export default chatService;