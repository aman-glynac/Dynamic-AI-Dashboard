'use client';

import React, { useEffect } from 'react';
import { DashboardCanvas } from '@/components/dashboard/DashboardCanvas';
import { useDashboardStore } from '@/store';

export default function HomePage() {
  const { createDashboard, currentDashboard } = useDashboardStore();

  useEffect(() => {
    // Create a default dashboard if none exists
    if (!currentDashboard) {
      createDashboard('My Dashboard', 4);
    }
  }, [currentDashboard, createDashboard]);

  return (
    <main className="h-screen w-full">
      <DashboardCanvas />
    </main>
  );
}