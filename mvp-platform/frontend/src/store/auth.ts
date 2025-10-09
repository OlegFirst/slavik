/**
 * Auth Store (Zustand)
 */

import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  full_name?: string;
  role: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string, organizationName?: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email: string, password: string) => {
    const { api } = await import('@/lib/api');
    const response = await api.login(email, password);
    localStorage.setItem('access_token', response.access_token);

    // Get user profile
    const userProfile = await api.getMe();
    set({ user: userProfile, isAuthenticated: true });
  },

  register: async (email: string, password: string, fullName?: string, organizationName?: string) => {
    const { api } = await import('@/lib/api');
    const response = await api.register(email, password, fullName, organizationName);
    localStorage.setItem('access_token', response.access_token);

    // Get user profile
    const userProfile = await api.getMe();
    set({ user: userProfile, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, isAuthenticated: false });
  },

  setUser: (user: User) => {
    set({ user, isAuthenticated: true, isLoading: false });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, isLoading: false });
      return;
    }

    try {
      const { api } = await import('@/lib/api');
      const userProfile = await api.getMe();
      set({ user: userProfile, isAuthenticated: true, isLoading: false });
    } catch (error) {
      localStorage.removeItem('access_token');
      set({ isAuthenticated: false, isLoading: false });
    }
  },
}));
