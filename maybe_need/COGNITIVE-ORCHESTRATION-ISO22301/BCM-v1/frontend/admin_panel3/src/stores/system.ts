import { create } from 'zustand';
import { AIOrgan, SystemMetrics, ServiceInfo } from '@/services/bcm';

interface SystemStore {
  // AI Organisms
  aiOrgans: AIOrgan[];
  setAIOrgans: (organs: AIOrgan[]) => void;
  
  // System metrics
  systemMetrics: SystemMetrics | null;
  setSystemMetrics: (metrics: SystemMetrics) => void;
  
  // Services
  services: ServiceInfo[];
  setServices: (services: ServiceInfo[]) => void;
  
  // Loading states
  loading: {
    organs: boolean;
    metrics: boolean;
    services: boolean;
  };
  setLoading: (key: keyof typeof loading, value: boolean) => void;
  
  // Errors
  errors: {
    organs: string | null;
    metrics: string | null;
    services: string | null;
  };
  setError: (key: keyof typeof errors, error: string | null) => void;
}

const loading = {
  organs: false,
  metrics: false,
  services: false,
};

const errors = {
  organs: null,
  metrics: null,
  services: null,
};

export const useSystemStore = create<SystemStore>((set) => ({
  aiOrgans: [],
  setAIOrgans: (organs) => set({ aiOrgans: organs }),
  
  systemMetrics: null,
  setSystemMetrics: (metrics) => set({ systemMetrics: metrics }),
  
  services: [],
  setServices: (services) => set({ services }),
  
  loading,
  setLoading: (key, value) => 
    set((state) => ({
      loading: { ...state.loading, [key]: value }
    })),
  
  errors,
  setError: (key, error) => 
    set((state) => ({
      errors: { ...state.errors, [key]: error }
    })),
}));

interface AppStore {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  
  refreshInterval: number;
  setRefreshInterval: (interval: number) => void;
  
  autoRefresh: boolean;
  setAutoRefresh: (enabled: boolean) => void;
  
  notifications: Array<{
    id: string;
    type: 'info' | 'success' | 'warning' | 'error';
    title: string;
    message: string;
    timestamp: Date;
  }>;
  addNotification: (notification: Omit<AppStore['notifications'][0], 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useAppStore = create<AppStore>((set) => ({
  activeTab: 'organisms',
  setActiveTab: (tab) => set({ activeTab: tab }),
  
  refreshInterval: 30000, // 30 seconds
  setRefreshInterval: (interval) => set({ refreshInterval: interval }),
  
  autoRefresh: true,
  setAutoRefresh: (enabled) => set({ autoRefresh: enabled }),
  
  notifications: [],
  addNotification: (notification) => 
    set((state) => ({
      notifications: [
        ...state.notifications,
        {
          ...notification,
          id: Math.random().toString(36).substr(2, 9),
          timestamp: new Date()
        }
      ]
    })),
  removeNotification: (id) => 
    set((state) => ({
      notifications: state.notifications.filter(n => n.id !== id)
    })),
  
  theme: 'light',
  setTheme: (theme) => set({ theme }),
}));
