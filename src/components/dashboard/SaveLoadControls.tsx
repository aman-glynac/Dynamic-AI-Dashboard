'use client';

import React, { useState } from 'react';
import { useDashboardStore } from '@/store';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Save, 
  FolderOpen, 
  FileText, 
  Trash2, 
  Download,
  Upload,
  MoreVertical 
} from 'lucide-react';

export function SaveLoadControls() {
  const {
    currentDashboard,
    dashboards,
    hasUnsavedChanges,
    saveDashboard,
    createDashboard,
    resetDashboard,
    isLoading,
  } = useDashboardStore();

  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [dashboardTitle, setDashboardTitle] = useState('');
  const [dashboardDescription, setDashboardDescription] = useState('');

  const handleSave = async () => {
    if (!currentDashboard) {
      // Create new dashboard
      createDashboard(dashboardTitle || 'Untitled Dashboard');
    }
    
    await saveDashboard();
    setShowSaveDialog(false);
    setDashboardTitle('');
    setDashboardDescription('');
  };

  const handleNew = () => {
    resetDashboard();
    createDashboard('New Dashboard');
  };

  return (
    <div className="flex items-center gap-2">
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
                        <span>Modified {dashboard.updatedAt.toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          // Load dashboard logic here
                          setShowLoadDialog(false);
                        }}
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
                          <DropdownMenuItem className="text-destructive">
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
          </div>
        </DialogContent>
      </Dialog>

      {/* New Dashboard */}
      <Button variant="outline" size="sm" onClick={handleNew}>
        <FileText className="w-4 h-4 mr-1" />
        New
      </Button>

      {/* Import/Export Menu */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem>
            <Upload className="w-4 h-4 mr-2" />
            Import Dashboard
          </DropdownMenuItem>
          <DropdownMenuItem disabled={!currentDashboard}>
            <Download className="w-4 h-4 mr-2" />
            Export Dashboard
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}