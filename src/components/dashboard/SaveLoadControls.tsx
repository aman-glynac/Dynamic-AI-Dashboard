'use client';

import React, { useState } from 'react';
import { useDashboardStore, useUIStore } from '@/store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  Save, 
  FolderOpen, 
  Download, 
  Trash2, 
  MoreVertical,
  FileText,
  AlertCircle
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

export function SaveLoadControls() {
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [dashboardTitle, setDashboardTitle] = useState('');
  const [dashboardDescription, setDashboardDescription] = useState('');
  
  const {
    currentDashboard,
    dashboards,
    saveDashboard,
    loadDashboard,
    deleteDashboard,
    isLoading,
    error,
    hasUnsavedChanges,
  } = useDashboardStore();

  const { addNotification } = useUIStore();

  const handleSave = async () => {
    try {
      const title = dashboardTitle || currentDashboard?.title || 'Untitled Dashboard';
      const description = dashboardDescription || currentDashboard?.description || '';
      
      await saveDashboard(title, description);
      
      addNotification({
        type: 'success',
        title: 'Dashboard Saved',
        message: `"${title}" has been saved successfully.`,
      });
      
      setShowSaveDialog(false);
      setDashboardTitle('');
      setDashboardDescription('');
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Save Failed',
        message: 'Failed to save dashboard. Please try again.',
      });
    }
  };

  const handleLoad = async (dashboardId: string) => {
    try {
      await loadDashboard(dashboardId);
      setShowLoadDialog(false);
      
      addNotification({
        type: 'success',
        title: 'Dashboard Loaded',
        message: 'Dashboard loaded successfully.',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Load Failed',
        message: 'Failed to load dashboard. Please try again.',
      });
    }
  };

  const handleDelete = async (dashboardId: string) => {
    if (confirm('Are you sure you want to delete this dashboard?')) {
      try {
        await deleteDashboard(dashboardId);
        
        addNotification({
          type: 'success',
          title: 'Dashboard Deleted',
          message: 'Dashboard deleted successfully.',
        });
      } catch (error) {
        addNotification({
          type: 'error',
          title: 'Delete Failed',
          message: 'Failed to delete dashboard. Please try again.',
        });
      }
    }
  };

  return (
    <>
      {/* Save Controls */}
      <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
        <DialogTrigger asChild>
          <Button
            variant={hasUnsavedChanges ? 'default' : 'outline'}
            size="sm"
            disabled={isLoading}
          >
            <Save className="w-4 h-4 mr-1" />
            {currentDashboard ? 'Save' : 'Save As'}
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {currentDashboard ? 'Save Dashboard' : 'Save New Dashboard'}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Dashboard Title</Label>
              <Input
                id="title"
                value={dashboardTitle || currentDashboard?.title || ''}
                onChange={(e) => setDashboardTitle(e.target.value)}
                placeholder="Enter dashboard title"
              />
            </div>
            <div>
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                value={dashboardDescription || currentDashboard?.description || ''}
                onChange={(e) => setDashboardDescription(e.target.value)}
                placeholder="Describe your dashboard"
                rows={3}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setShowSaveDialog(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={isLoading || (!dashboardTitle && !currentDashboard)}
              >
                {isLoading ? 'Saving...' : 'Save Dashboard'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Load Controls */}
      <Dialog open={showLoadDialog} onOpenChange={setShowLoadDialog}>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm">
            <FolderOpen className="w-4 h-4 mr-1" />
            Load
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Load Dashboard</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {dashboards.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No saved dashboards found</p>
                <p className="text-sm">Create and save your first dashboard to see it here</p>
              </div>
            ) : (
              <div className="grid gap-3 max-h-96 overflow-y-auto">
                {dashboards.map((dashboard) => (
                  <div
                    key={dashboard.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
                  >
                    <div className="flex-1">
                      <h4 className="font-medium">{dashboard.title}</h4>
                      <p className="text-sm text-muted-foreground">
                        {dashboard.description || 'No description'}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
                        <span>{dashboard.containerCount} containers</span>
                        <span>{dashboard.chartCount} charts</span>
                        <span>Modified {new Date(dashboard.updatedAt).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleLoad(dashboard.id)}
                      >
                        Load
                      </Button>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Download className="w-4 h-4 mr-2" />
                            Export
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="text-destructive"
                            onClick={() => handleDelete(dashboard.id)}
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}