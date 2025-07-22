import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { DataSourceConfig } from '@/types';

interface DataStore {
  // State
  dataSources: Record<string, DataSourceConfig>;
  connectionStatus: Record<string, 'connected' | 'disconnected' | 'error'>;
  lastUpdated: Record<string, Date>;

  // Actions
  addDataSource: (dataSource: DataSourceConfig) => void;
  updateDataSource: (id: string, updates: Partial<DataSourceConfig>) => void;
  removeDataSource: (id: string) => void;
  setConnectionStatus: (id: string, status: 'connected' | 'disconnected' | 'error') => void;
  setLastUpdated: (id: string, date: Date) => void;
}

export const useDataStore = create<DataStore>()(
  devtools(
    (set) => ({
      // Initial state
      dataSources: {},
      connectionStatus: {},
      lastUpdated: {},

      // Actions
      addDataSource: (dataSource: DataSourceConfig) => {
        set(state => ({
          dataSources: {
            ...state.dataSources,
            [dataSource.id]: dataSource,
          },
          connectionStatus: {
            ...state.connectionStatus,
            [dataSource.id]: 'disconnected',
          },
        }));
      },

      updateDataSource: (id: string, updates: Partial<DataSourceConfig>) => {
        set(state => ({
          dataSources: {
            ...state.dataSources,
            [id]: {
              ...state.dataSources[id]!,
              ...updates,
            },
          },
        }));
      },

      removeDataSource: (id: string) => {
        set(state => {
          const { [id]: removed, ...remainingDataSources } = state.dataSources;
          const { [id]: removedStatus, ...remainingStatus } = state.connectionStatus;
          const { [id]: removedUpdated, ...remainingUpdated } = state.lastUpdated;

          return {
            dataSources: remainingDataSources,
            connectionStatus: remainingStatus,
            lastUpdated: remainingUpdated,
          };
        });
      },

      setConnectionStatus: (id: string, status: 'connected' | 'disconnected' | 'error') => {
        set(state => ({
          connectionStatus: {
            ...state.connectionStatus,
            [id]: status,
          },
        }));
      },

      setLastUpdated: (id: string, date: Date) => {
        set(state => ({
          lastUpdated: {
            ...state.lastUpdated,
            [id]: date,
          },
        }));
      },
    }),
    { name: 'data-store' }
  )
);