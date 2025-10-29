import { create } from 'zustand'

// Global BCM Platform Store
interface BCMStore {
  // User state
  user: any | null
  setUser: (user: any) => void

  // Navigation state
  currentModule: string
  setCurrentModule: (module: string) => void

  // Notifications
  notifications: any[]
  addNotification: (notification: any) => void
  removeNotification: (id: string) => void

  // Loading states
  isLoading: boolean
  setLoading: (loading: boolean) => void
}

export const useBCMStore = create<BCMStore>((set) => ({
  // User state
  user: null,
  setUser: (user) => set({ user }),

  // Navigation state
  currentModule: 'dashboard',
  setCurrentModule: (currentModule) => set({ currentModule }),

  // Notifications
  notifications: [],
  addNotification: (notification) =>
    set((state) => ({
      notifications: [...state.notifications, { ...notification, id: Date.now().toString() }]
    })),
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter(n => n.id !== id)
    })),

  // Loading states
  isLoading: false,
  setLoading: (isLoading) => set({ isLoading }),
}))