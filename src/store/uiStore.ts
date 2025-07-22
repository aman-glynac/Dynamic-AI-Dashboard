import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { Mode, Notification } from '@/types';
import { generateId } from '@/lib/utils';

interface UIStore {
  // State
  mode: Mode;
  selectedContainerId?: number;
  isGenerating: boolean;
  notifications: Notification[];
  sidebarOpen: boolean;

  // Actions
  setMode: (mode: Mode) => void;
  setSelectedContainer: (containerId?: number) => void;
  setGenerating: (isGenerating: boolean) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      mode: 'edit',
      notifications: [],
      sidebarOpen: false,
      isGenerating: false,

      // Actions
      setMode: (mode: Mode) => {
        set({ mode });
      },

      setSelectedContainer: (containerId?: number) => {
        set({ selectedContainerId: containerId });
      },

      setGenerating: (isGenerating: boolean) => {
        set({ isGenerating });
      },

      addNotification: (notification) => {
        const newNotification: Notification = {
          ...notification,
          id: generateId(),
          createdAt: new Date(),
        };

        set(state => ({
          notifications: [...state.notifications, newNotification],
        }));

        // Auto-remove notification after duration (default 5 seconds)
        const duration = notification.duration || 5000;
        setTimeout(() => {
          get().removeNotification(newNotification.id);
        }, duration);
      },

      removeNotification: (id: string) => {
        set(state => ({
          notifications: state.notifications.filter(n => n.id !== id),
        }));
      },

      clearNotifications: () => {
        set({ notifications: [] });
      },

      toggleSidebar: () => {
        set(state => ({ sidebarOpen: !state.sidebarOpen }));
      },
    }),
    { name: 'ui-store' }
  )
);