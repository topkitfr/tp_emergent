import axios from 'axios';

// Get API URL from environment
const API_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://football-db.preview.emergentagent.com';

class TokenManager {
  constructor() {
    this.refreshPromise = null;
  }

  // Get token from localStorage
  getToken() {
    return localStorage.getItem('token');
  }

  // Save token to localStorage
  saveToken(token) {
    localStorage.setItem('token', token);
  }

  // Remove token from localStorage
  removeToken() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  }

  // Create axios instance with automatic token refresh
  createAxiosInstance() {
    const instance = axios.create({
      baseURL: API_URL
    });

    // Request interceptor to add token
    instance.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    instance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshToken();
            if (newToken) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return instance(originalRequest);
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            this.removeToken();
            // Redirect to login or show auth modal
            window.location.reload();
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );

    return instance;
  }

  // Refresh token
  async refreshToken() {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const token = this.getToken();
    if (!token) {
      throw new Error('No token to refresh');
    }

    this.refreshPromise = this.performTokenRefresh(token);
    
    try {
      const result = await this.refreshPromise;
      return result;
    } finally {
      this.refreshPromise = null;
    }
  }

  async performTokenRefresh(token) {
    try {
      console.log('🔄 Refreshing token...');
      
      const response = await axios.post(
        `${API_URL}/api/auth/refresh-token`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (response.data.token) {
        console.log('✅ Token refreshed successfully');
        this.saveToken(response.data.token);
        
        // Update user data if provided
        if (response.data.user) {
          localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        
        return response.data.token;
      }
      
      throw new Error('No token in refresh response');
    } catch (error) {
      console.error('❌ Token refresh failed:', error);
      throw error;
    }
  }

  // Make authenticated API call with automatic refresh
  async makeAuthenticatedRequest(method, url, data = null, config = {}) {
    const axiosInstance = this.createAxiosInstance();
    
    try {
      let response;
      
      switch (method.toLowerCase()) {
        case 'get':
          response = await axiosInstance.get(url, config);
          break;
        case 'post':
          response = await axiosInstance.post(url, data, config);
          break;
        case 'put':
          response = await axiosInstance.put(url, data, config);
          break;
        case 'delete':
          response = await axiosInstance.delete(url, config);
          break;
        default:
          throw new Error(`Unsupported method: ${method}`);
      }
      
      return response;
    } catch (error) {
      console.error(`❌ API request failed (${method.toUpperCase()} ${url}):`, error);
      throw error;
    }
  }
}

// Create singleton instance
const tokenManager = new TokenManager();

export default tokenManager;