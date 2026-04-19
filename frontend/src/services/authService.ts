import apiClient from './apiClient';

const AUTH_TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_ROLE_KEY = 'user_role';

// Matches the backend API response shape exactly
export interface AuthResponse {
  token: string;
  refresh_token?: string;
  role: 'worker' | 'verifier' | 'advocate';
  user_id: string;
  expires_in: number;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  role: 'worker' | 'verifier' | 'advocate';
  full_name?: string;
  platform?: string;
  city_zone?: string;
}

export interface OTPVerifyPayload {
  email: string;
  otp: string;
}

export const authService = {
  setAuthToken: (token: string) => {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  },

  getAuthToken: (): string | null => {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  },

  setRefreshToken: (token: string) => {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  },

  getRefreshToken: (): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  setUserRole: (role: string) => {
    localStorage.setItem(USER_ROLE_KEY, role);
  },

  getUserRole: (): string | null => {
    return localStorage.getItem(USER_ROLE_KEY);
  },

  logout: () => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_ROLE_KEY);
  },

  login: async (payload: LoginPayload): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', payload);
    authService.setAuthToken(response.data.token);
    if (response.data.refresh_token) {
      authService.setRefreshToken(response.data.refresh_token);
    }
    authService.setUserRole(response.data.role);
    return response.data;
  },

  register: async (payload: RegisterPayload): Promise<{ requires_otp: boolean; otp_sent_to: string }> => {
    const response = await apiClient.post<{ requires_otp: boolean; otp_sent_to: string }>(
      '/auth/register',
      payload
    );
    return response.data;
  },

  sendOTP: async (email: string): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>('/auth/otp/send', { email });
    return response.data;
  },

  verifyOTP: async (payload: OTPVerifyPayload): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/otp/verify', payload);
    authService.setAuthToken(response.data.token);
    if (response.data.refresh_token) {
      authService.setRefreshToken(response.data.refresh_token);
    }
    authService.setUserRole(response.data.role);
    return response.data;
  },

  refreshToken: async (): Promise<string | null> => {
    try {
      const storedRefreshToken = authService.getRefreshToken();
      if (!storedRefreshToken) {
        return null;
      }
      const response = await apiClient.post<{ token: string; expires_in: number }>(
        '/auth/refresh',
        { refresh_token: storedRefreshToken }
      );
      authService.setAuthToken(response.data.token);
      return response.data.token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      authService.logout();
      return null;
    }
  },

  forgotPassword: async (email: string): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>('/auth/forgot-password', { email });
    return response.data;
  },

  resetPassword: async (token: string, newPassword: string): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>('/auth/reset-password', {
      token,
      new_password: newPassword,
    });
    return response.data;
  },

  verifyToken: async (): Promise<{ valid: boolean; role: string }> => {
    const response = await apiClient.get<{ valid: boolean; role: string }>('/auth/verify');
    return response.data;
  },

  isAuthenticated: (): boolean => {
    return !!authService.getAuthToken();
  },
};

// Named exports for convenience
export const getAuthToken = authService.getAuthToken;
export const setAuthToken = authService.setAuthToken;
export const getUserRole = authService.getUserRole;
export const logout = authService.logout;
export const refreshToken = authService.refreshToken;
