import axios from 'axios';
import { User, SignupData, ProfileData } from '../contexts/authContext';

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

export interface LoginResponse {
  user: User;
  token: string;
  refreshToken?: string;
}

export const authService = {
  // Login user
  async login(phone: string, password: string): Promise<LoginResponse> {
    try {
      const response = await apiClient.post('/api/auth/login/', { phone, password });
      const { user, token, refreshToken } = response.data;
      
      // Store token and user data
      localStorage.setItem('authToken', token);
      if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken);
      }
      localStorage.setItem('user', JSON.stringify(user));
      
      return { user, token, refreshToken };
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Register new user
  async signup(userData: SignupData): Promise<LoginResponse> {
    try {
      const response = await apiClient.post('/api/auth/signup/', userData);
      const { user, token, refreshToken } = response.data;
      
      // Store token and user data
      localStorage.setItem('authToken', token);
      if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken);
      }
      localStorage.setItem('user', JSON.stringify(user));
      
      return { user, token, refreshToken };
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Logout user
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout/');
    } catch (error) {
      // Even if logout request fails, clear local storage
      console.error('Logout request failed:', error);
    } finally {
      // Clear local storage
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    }
  },

  // Refresh token
  async refreshToken(): Promise<string> {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post('/auth/refresh/', { refreshToken });
      const { token } = response.data;
      
      localStorage.setItem('authToken', token);
      return token;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Get current user from local storage
  getCurrentUser(): User | null {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('authToken');
  },

  // Get user profile
  async getProfile(): Promise<User> {
    try {
      const response = await apiClient.get('/api/auth/profile/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Update user profile
  async updateProfile(profileData: ProfileData): Promise<User> {
    try {
      const response = await apiClient.post('/api/auth/profile/', profileData);
      
      // Update user data in local storage
      localStorage.setItem('user', JSON.stringify(response.data));
      
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
        const message = error.response.data?.message || 'Server error occurred';
        return new Error(message);
      } else if (error.request) {
        // Request was made but no response received
        return new Error('Network error. Please check your connection.');
      } else {
        // Something else happened in setting up the request
        return new Error(error.message || 'An unexpected error occurred');
      }
    } else if (error instanceof Error) {
      // Generic JavaScript error
      return error;
    } else {
      // Unknown error type
      return new Error('An unexpected error occurred');
    }
  },
};

export default authService;