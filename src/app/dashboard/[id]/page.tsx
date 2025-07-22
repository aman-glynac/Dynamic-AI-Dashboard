'use client';

import React, { useEffect } from 'react';
import { useParams } from 'next/navigation';
import { DashboardCanvas } from '@/components/dashboard/DashboardCanvas';
import { useDashboardStore } from '@/store';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

export default function DashboardPage() {
  const params = useParams();
  const dashboardId = params.id as string;
  
  const { 
    currentDashboard, 
    loadDashboard, 
    isLoading, 
    error 
  } = useDashboardStore();

  useEffect(() => {
    if (dashboardId && (!currentDashboard || currentDashboard.id !== dashboardId)) {
      // In a real app, you would fetch the dashboard by ID here
      // For now, we'll just ensure we have a dashboard loaded
      console.log('Loading dashboard:', dashboardId);
    }
  }, [dashboardId, currentDashboard, loadDashboard]);

  if (isLoading) {
    return (
      <main className="h-screen w-full">
        <div className="flex items-center justify-center h-full">
          <LoadingSpinner size="lg" text="Loading dashboard..." />
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="h-screen w-full">
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4 text-destructive">Error</h1>
            <p className="text-muted-foreground mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="h-screen w-full">
      <DashboardCanvas />
    </main>
  );
}