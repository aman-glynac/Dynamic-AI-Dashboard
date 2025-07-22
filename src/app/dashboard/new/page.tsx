'use client';

import React, { useEffect } from 'react';
import { useDashboardStore } from '@/store';
import { useRouter } from 'next/navigation';

export default function NewDashboardPage() {
  const { createDashboard, currentDashboard } = useDashboardStore();
  const router = useRouter();

  useEffect(() => {
    // Create a new dashboard
    createDashboard('New Dashboard', 1);
  }, [createDashboard]);

  useEffect(() => {
    // Redirect to dashboard ID once created
    if (currentDashboard) {
      router.push(`/dashboard/${currentDashboard.id}`);
    }
  }, [currentDashboard, router]);

  return (
    <main className="h-screen w-full">
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Creating New Dashboard...</h1>
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    </main>
  );
}
