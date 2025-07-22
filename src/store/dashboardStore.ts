import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { Dashboard, DashboardMetadata } from '@/types/dashboard';
import { GridConfig, ContainerConfig } from '@/types/container';
import { Mode } from '@/types/common';

interface DashboardStore {
  // State
  currentDashboard?: Dashboard;
  dashboards: DashboardMetadata[];
  gridConfig: GridConfig;
  isLoading: boolean;
  error?: string;
  hasUnsavedChanges: boolean;

  // Actions
  createDashboard: (title: string, containerCount?: number) => void;
  loadDashboard: (dashboard: Dashboard) => void;
  updateDashboard: (updates: Partial<Dashboard>) => void;
  saveDashboard: () => Promise<void>;
  deleteDashboard: (id: string) => void;
  setGridConfig: (config: GridConfig) => void;
  updateContainer: (containerId: number, updates: Partial<ContainerConfig>) => void;
  setContainerCount: (count: number) => void;
  setMode: (mode: Mode) => void;
  markAsChanged: () => void;
  clearError: () => void;
  resetDashboard: () => void;
}

const createInitialGridConfig = (containerCount: number = 1): GridConfig => {
  const containers: ContainerConfig[] = [];
  
  // Calculate grid layout based on container count
  const cols = Math.ceil(Math.sqrt(containerCount));
  const rows = Math.ceil(containerCount / cols);
  
  for (let i = 0; i < containerCount; i++) {
    const row = Math.floor(i / cols);
    const col = i % cols;
    
    containers.push({
      id: i + 1,
      layout: {
        id: i + 1,
        x: col,
        y: row,
        width: 1,
        height: 1,
        minWidth: 1,
        minHeight: 1,
      },
      isEmpty: true,
    });
  }

  return {
    containerCount,
    containers,
    mode: 'edit',
  };
};

function generateId(): string {
  return Math.random().toString(36).substr(2, 9);
}

export const useDashboardStore = create<DashboardStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        dashboards: [],
        gridConfig: createInitialGridConfig(1),
        isLoading: false,
        hasUnsavedChanges: false,

        // Actions
        createDashboard: (title: string, containerCount = 1) => {
          const newDashboard: Dashboard = {
            id: generateId(),
            title,
            gridConfig: createInitialGridConfig(containerCount),
            charts: {},
            createdAt: new Date(),
            updatedAt: new Date(),
            isPublic: false,
            version: 1,
          };

          set({
            currentDashboard: newDashboard,
            gridConfig: newDashboard.gridConfig,
            hasUnsavedChanges: true,
          });
        },

        loadDashboard: (dashboard: Dashboard) => {
          set({
            currentDashboard: dashboard,
            gridConfig: dashboard.gridConfig,
            hasUnsavedChanges: false,
          });
        },

        updateDashboard: (updates: Partial<Dashboard>) => {
          const current = get().currentDashboard;
          if (!current) return;

          const updatedDashboard = {
            ...current,
            ...updates,
            updatedAt: new Date(),
            version: current.version + 1,
          };

          set({
            currentDashboard: updatedDashboard,
            hasUnsavedChanges: true,
          });
        },

        saveDashboard: async () => {
          const { currentDashboard } = get();
          if (!currentDashboard) return;

          set({ isLoading: true });

          try {
            // Here you would call your API to save the dashboard
            // For now, we'll just simulate saving
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            set({ 
              hasUnsavedChanges: false,
              isLoading: false,
            });
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Failed to save dashboard',
              isLoading: false,
            });
          }
        },

        deleteDashboard: (id: string) => {
          set(state => {
            const newState = {
              ...state,
              dashboards: state.dashboards.filter(d => d.id !== id),
            };
            
            if (state.currentDashboard?.id === id) {
              return {
                ...newState,
                gridConfig: createInitialGridConfig(1),
                hasUnsavedChanges: false,
              };
            }
            
            return newState;
          });
        },

        setGridConfig: (config: GridConfig) => {
          set({ 
            gridConfig: config,
            hasUnsavedChanges: true,
          });
          
          // Also update the current dashboard if it exists
          const { updateDashboard } = get();
          updateDashboard({ gridConfig: config });
        },

        updateContainer: (containerId: number, updates: Partial<ContainerConfig>) => {
          const { gridConfig, setGridConfig } = get();
          
          const updatedContainers = gridConfig.containers.map(container =>
            container.id === containerId
              ? { ...container, ...updates }
              : container
          );

          setGridConfig({
            ...gridConfig,
            containers: updatedContainers,
          });
        },

        setContainerCount: (count: number) => {
          if (count < 1 || count > 10) return;
          
          const { gridConfig, setGridConfig } = get();
          const newGridConfig = createInitialGridConfig(count);
          
          // Preserve existing containers and their charts if possible
          const existingContainers = gridConfig.containers.slice(0, count);
          const newContainers = newGridConfig.containers.slice(existingContainers.length);
          
          setGridConfig({
            ...newGridConfig,
            containers: [...existingContainers, ...newContainers],
          });
        },

        setMode: (mode: Mode) => {
          const { gridConfig, setGridConfig } = get();
          setGridConfig({ ...gridConfig, mode });
        },

        markAsChanged: () => {
          set({ hasUnsavedChanges: true });
        },

        clearError: () => {
          set({ error: '' });
        },

        resetDashboard: () => {
          set({
            gridConfig: createInitialGridConfig(1),
            hasUnsavedChanges: false,
          });
        },
      }),
      {
        name: 'dashboard-store',
        partialize: (state) => ({
          currentDashboard: state.currentDashboard,
          gridConfig: state.gridConfig,
          hasUnsavedChanges: state.hasUnsavedChanges,
        }),
      }
    ),
    { name: 'dashboard-store' }
  )
);
