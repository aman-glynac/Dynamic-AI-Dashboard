'use client'

import React, { useState, useEffect, useRef } from 'react'
import ComponentRenderer from './ComponentRenderer'
import { apiService } from '@/services/api'
import toast from 'react-hot-toast'

interface ChartState {
  componentCode: string | null
  componentName: string | null
  isLoading: boolean
  jobId: string | null
  progress: number
}

export default function Canvas() {
  const [chartState, setChartState] = useState<ChartState>({
    componentCode: null,
    componentName: null,
    isLoading: false,
    jobId: null,
    progress: 0
  })

  const [databaseStatus, setDatabaseStatus] = useState<{
    totalTables: number
    hasData: boolean
  }>({ totalTables: 0, hasData: false })

  // Use ref to store the function instead of window global
  const chartGenerationRef = useRef<((prompt: string) => Promise<void>) | null>(null)

  // Check database status on mount
  useEffect(() => {
    const checkDatabaseStatus = async () => {
      try {
        const status = await apiService.getDatabaseStatus()
        setDatabaseStatus({
          totalTables: status.total_tables,
          hasData: status.total_tables > 0
        })
      } catch (error) {
        console.error('Failed to check database status:', error)
      }
    }

    checkDatabaseStatus()
  }, [])

  const handleChartGeneration = async (prompt: string) => {
    try {
      setChartState(prev => ({
        ...prev,
        isLoading: true,
        progress: 0,
        componentCode: null,
        componentName: null
      }))

      // Start chart generation
      const jobResponse = await apiService.generateChart({ prompt })
      
      setChartState(prev => ({
        ...prev,
        jobId: jobResponse.job_id
      }))

      toast.success('Chart generation started!')

      // Poll for results
      const result = await apiService.pollJobStatus(
        jobResponse.job_id,
        (status) => {
          setChartState(prev => ({
            ...prev,
            progress: status.progress || 0
          }))

          // Show progress updates
          if (status.progress === 25) {
            toast.loading('Analyzing prompt...', { id: 'progress' })
          } else if (status.progress === 50) {
            toast.loading('Generating SQL...', { id: 'progress' })
          } else if (status.progress === 75) {
            toast.loading('Processing data...', { id: 'progress' })
          } else if (status.progress === 100) {
            toast.loading('Creating chart...', { id: 'progress' })
          }
        }
      )

      // Get final job status to extract component name and additional info
      const finalStatus = await apiService.getJobStatus(jobResponse.job_id)
      
      // Extract component name from the code using regex
      const extractComponentName = (code: string): string => {
        // Match pattern: const ComponentName = () => {
        const componentNameMatch = code.match(/const\s+(\w+)\s*=\s*\(\s*\)\s*=>\s*{/)
        if (componentNameMatch && componentNameMatch[1]) {
          return componentNameMatch[1]
        }
        
        // Fallback: try to match function ComponentName() {
        const functionMatch = code.match(/function\s+(\w+)\s*\(\s*\)/)
        if (functionMatch && functionMatch[1]) {
          return functionMatch[1]
        }
        
        // Last resort: find any PascalCase word that might be a component
        const pascalCaseMatch = code.match(/\b([A-Z][a-zA-Z]+(?:Chart|Component|View|Widget))\b/)
        if (pascalCaseMatch && pascalCaseMatch[1]) {
          return pascalCaseMatch[1]
        }
        
        return 'GeneratedChart'
      }
      
      // Extract chart type from component name or code
      const extractChartType = (componentName: string, code: string): string => {
        // Try to get from component name first
        const namePatterns = {
          'Bar': 'bar',
          'Line': 'line',
          'Pie': 'pie',
          'Scatter': 'scatter',
          'Area': 'area',
          'Radar': 'radar',
          'Table': 'table'
        }
        
        for (const [pattern, type] of Object.entries(namePatterns)) {
          if (componentName.includes(pattern)) {
            return type
          }
        }
        
        // Try to detect from code
        const codePatterns = {
          'BarChart': 'bar',
          'LineChart': 'line',
          'PieChart': 'pie',
          'ScatterChart': 'scatter',
          'AreaChart': 'area',
          'RadarChart': 'radar',
          '<table': 'table'
        }
        
        for (const [pattern, type] of Object.entries(codePatterns)) {
          if (code.includes(pattern)) {
            return type
          }
        }
        
        return 'chart'
      }
      
      const componentName = extractComponentName(result)
      const chartType = extractChartType(componentName, result)
      
      console.log('Full finalStatus:', finalStatus)
      console.log('Component code length:', result?.length)
      console.log('Extracted component name:', componentName)
      console.log('Detected chart type:', chartType)

      setChartState(prev => ({
        ...prev,
        componentCode: result,
        componentName: componentName,
        isLoading: false,
        progress: 100
      }))

      // Log the component for debugging
      console.log('Setting component:', {
        code: result?.substring(0, 500),
        name: componentName,
        type: chartType,
        fullResult: result
      })

      toast.dismiss('progress')
      toast.success('Chart generated successfully!')

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate chart'
      
      setChartState(prev => ({
        ...prev,
        isLoading: false,
        progress: 0,
        jobId: null
      }))

      toast.dismiss('progress')
      toast.error(errorMessage)
      console.error('Chart generation error:', error)
    }
  }

  // Store the function in ref and expose it globally
  useEffect(() => {
    chartGenerationRef.current = handleChartGeneration
    
    // Expose to window for PromptInput
    if (typeof window !== 'undefined') {
      (window as any).generateChart = handleChartGeneration
    }

    // Cleanup on unmount
    return () => {
      if (typeof window !== 'undefined') {
        delete (window as any).generateChart
      }
    }
  }, [])

  return (
    <div className="w-full h-full bg-gray-50 p-4 relative">
      {/* Database Status Banner */}
      {!databaseStatus.hasData && (
        <div className="absolute top-4 left-4 right-4 bg-yellow-100 border border-yellow-300 rounded-lg p-3 text-sm text-yellow-800 z-10">
          <strong>⚠️ No data available:</strong> Please process data files first to generate charts.
        </div>
      )}

      {/* Main Container */}
      <div 
        className={`w-full h-full border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center relative ${
          !databaseStatus.hasData ? 'mt-16' : ''
        }`}
        style={{ minHeight: '400px' }} 
      >
        {/* Loading State */}
        {chartState.isLoading && (
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <div className="text-lg font-medium text-gray-700 mb-2">Generating Chart...</div>
            <div className="text-sm text-gray-500 mb-3">
              {chartState.progress > 0 ? `${chartState.progress}% complete` : 'Starting...'}
            </div>
            <div className="w-64 bg-gray-200 rounded-full h-2 mx-auto">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${chartState.progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Chart Renderer */}
        {!chartState.isLoading && chartState.componentCode && chartState.componentName && (
          <ComponentRenderer 
            componentCode={chartState.componentCode}
            componentName={chartState.componentName}
          />
        )}

        {/* Empty State */}
        {!chartState.isLoading && !chartState.componentCode && (
          <div className="text-center">
            <div className="text-6xl font-bold text-gray-400 mb-2">1</div>
            <div className="text-gray-500 mb-2">Container 1</div>
            {databaseStatus.hasData && (
              <div className="text-xs text-gray-400">
                Ready for chart generation • {databaseStatus.totalTables} table{databaseStatus.totalTables !== 1 ? 's' : ''} available
              </div>
            )}
          </div>
        )}

        {/* Container Label */}
        {!chartState.isLoading && chartState.componentCode && (
          <div className="absolute top-2 left-2 bg-white bg-opacity-80 rounded px-2 py-1 text-xs text-gray-600">
            Container 1
          </div>
        )}
      </div>
    </div>
  )
}