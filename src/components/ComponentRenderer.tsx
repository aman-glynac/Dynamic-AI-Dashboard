'use client'

import React, { useState, useEffect, useRef } from 'react'
import * as Recharts from 'recharts'
import * as Babel from '@babel/standalone'
import toast from 'react-hot-toast'

interface ComponentRendererProps {
  componentCode: string
  componentName: string
}

// Make Recharts components available globally for the dynamic components
const rechartsComponents = {
  ResponsiveContainer: Recharts.ResponsiveContainer,
  BarChart: Recharts.BarChart,
  Bar: Recharts.Bar,
  LineChart: Recharts.LineChart,
  Line: Recharts.Line,
  AreaChart: Recharts.AreaChart,
  Area: Recharts.Area,
  PieChart: Recharts.PieChart,
  Pie: Recharts.Pie,
  Cell: Recharts.Cell,
  ScatterChart: Recharts.ScatterChart,
  Scatter: Recharts.Scatter,
  XAxis: Recharts.XAxis,
  YAxis: Recharts.YAxis,
  ZAxis: Recharts.ZAxis,
  CartesianGrid: Recharts.CartesianGrid,
  Tooltip: Recharts.Tooltip,
  Legend: Recharts.Legend,
  RadarChart: Recharts.RadarChart,
  Radar: Recharts.Radar,
  PolarGrid: Recharts.PolarGrid,
  PolarAngleAxis: Recharts.PolarAngleAxis,
  PolarRadiusAxis: Recharts.PolarRadiusAxis,
  ComposedChart: Recharts.ComposedChart,
  LabelList: Recharts.LabelList,
  // Add more as needed
}

export default function ComponentRenderer({ componentCode, componentName }: ComponentRendererProps) {
  const [RenderedComponent, setRenderedComponent] = useState<React.ComponentType | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const isMountedRef = useRef(true)

  useEffect(() => {
    // Track mounted state for cleanup
    isMountedRef.current = true
    
    return () => {
      isMountedRef.current = false
    }
  }, [])

  useEffect(() => {
    const renderComponent = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // Step 1: Clean the component code
        let cleanedCode = componentCode
          .replace(/import\s+.*?from\s+['"].*?['"];?\s*/g, '') // Remove all imports
          .replace(/export\s+default\s+.*?;?\s*$/gm, '') // Remove export statements
          .trim()

        // Step 2: Transform JSX to JavaScript using Babel
        let transformedCode: string
        try {
          const result = Babel.transform(cleanedCode, {
            presets: ['react'],
            plugins: [],
            filename: 'component.jsx'
          })
          
          if (!result.code) {
            throw new Error('Babel transformation returned no code')
          }
          
          transformedCode = result.code
        } catch (babelError: any) {
          console.error('Babel transformation error:', babelError)
          throw new Error(`JSX transformation failed: ${babelError.message}`)
        }

        // Step 3: Create a component factory function
        const componentFactory = (React: any, useState: any, useEffect: any, useRef: any, useMemo: any, useCallback: any, ...rechartsImports: any[]) => {
          try {
            // Create a wrapper to capture the component
            const exports: any = {}
            const module = { exports }
            
            // Build the execution context
            const executionCode = `
              ${transformedCode}
              
              // Try different ways to export the component
              if (typeof ${componentName} !== 'undefined') {
                return ${componentName};
              } else if (typeof exports.default !== 'undefined') {
                return exports.default;
              } else if (typeof module.exports !== 'undefined' && typeof module.exports === 'function') {
                return module.exports;
              } else if (typeof module.exports?.default === 'function') {
                return module.exports.default;
              } else {
                // Try to find any function that looks like a component
                const possibleComponents = Object.keys(this).filter(key => 
                  typeof this[key] === 'function' && 
                  key[0] === key[0].toUpperCase() &&
                  key !== 'React'
                );
                if (possibleComponents.length > 0) {
                  return this[possibleComponents[0]];
                }
                throw new Error('No component found');
              }
            `

            // Create a function with all the dependencies injected
            const func = new Function(
              'React', 'useState', 'useEffect', 'useRef', 'useMemo', 'useCallback',
              'ResponsiveContainer', 'BarChart', 'Bar', 'LineChart', 'Line',
              'AreaChart', 'Area', 'PieChart', 'Pie', 'Cell',
              'ScatterChart', 'Scatter', 'XAxis', 'YAxis', 'ZAxis',
              'CartesianGrid', 'Tooltip', 'Legend', 'RadarChart', 'Radar',
              'PolarGrid', 'PolarAngleAxis', 'PolarRadiusAxis', 'ComposedChart', 'LabelList',
              'exports', 'module',
              executionCode
            )

            // Execute with all dependencies
            const Component = func(
              React, React.useState, React.useEffect, React.useRef, React.useMemo, React.useCallback,
              ...Object.values(rechartsComponents),
              exports, module
            )

            return Component
          } catch (execError: any) {
            console.error('Component execution error:', execError)
            throw execError
          }
        }

        // Step 4: Execute the factory to get the component
        const Component = componentFactory(
          React,
          React.useState,
          React.useEffect, 
          React.useRef,
          React.useMemo,
          React.useCallback,
          ...Object.values(rechartsComponents)
        )

        // Step 5: Validate the component
        if (typeof Component !== 'function') {
          throw new Error(`Expected a React component function but got ${typeof Component}`)
        }

        // Log the component for debugging
        console.log('Generated Component:', Component)
        console.log('Component code preview:', componentCode.substring(0, 200) + '...')

        // Step 6: Create a wrapper component with error boundary and debugging
        const SafeComponent = () => {
          const [hasError, setHasError] = useState(false)
          const [debugInfo, setDebugInfo] = useState<string>('')

          // Simple error boundary using useEffect
          useEffect(() => {
            const handleError = (event: ErrorEvent) => {
              console.error('Component runtime error:', event.error)
              setHasError(true)
              event.preventDefault()
            }

            window.addEventListener('error', handleError)
            return () => window.removeEventListener('error', handleError)
          }, [])

          if (hasError) {
            return (
              <div className="w-full h-full flex items-center justify-center p-4">
                <div className="text-center bg-red-50 border border-red-200 rounded-lg p-6">
                  <div className="text-red-500 text-2xl mb-2">⚠️</div>
                  <div className="text-red-700 font-medium">Component Runtime Error</div>
                  <div className="text-red-600 text-sm mt-2">The chart encountered an error while rendering</div>
                  {debugInfo && (
                    <div className="mt-2 text-xs text-gray-600 bg-gray-100 p-2 rounded">
                      {debugInfo}
                    </div>
                  )}
                </div>
              </div>
            )
          }

          try {
            console.log('Attempting to render component...')
            const result = <Component />
            console.log('Component rendered, result:', result)
            
            // Debug: Check what the component actually rendered
            if (result && result.props) {
              console.log('Component props:', result.props)
              console.log('Component type:', result.type)
            }
            
            // Check if component returned null or undefined
            if (!result) {
              console.warn('Component returned null or undefined')
              return (
                <div className="w-full h-full flex items-center justify-center p-4">
                  <div className="text-center bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <div className="text-yellow-500 text-2xl mb-2">⚠️</div>
                    <div className="text-yellow-700 font-medium">Empty Component</div>
                    <div className="text-yellow-600 text-sm mt-2">The component rendered but returned no content</div>
                    <details className="mt-3 text-left">
                      <summary className="cursor-pointer text-xs text-gray-600 hover:text-gray-800">View Debug Info</summary>
                      <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto max-h-40">
                        {componentCode}
                      </pre>
                    </details>
                  </div>
                </div>
              )
            }
            
            return result
          } catch (renderError: any) {
            console.error('Component render error:', renderError)
            setDebugInfo(renderError.toString())
            setHasError(true)
            return null
          }
        }

        // Only update state if component is still mounted
        if (isMountedRef.current) {
          setRenderedComponent(() => SafeComponent)
        }

      } catch (err: any) {
        const errorMessage = err.message || 'Failed to render component'
        console.error('Component rendering error:', err)
        
        // Only update state if component is still mounted
        if (isMountedRef.current) {
          setError(errorMessage)
          toast.error(`Failed to render chart: ${errorMessage}`)
        }
      } finally {
        if (isMountedRef.current) {
          setIsLoading(false)
        }
      }
    }

    if (componentCode && componentName) {
      renderComponent()
    }
  }, [componentCode, componentName])

  if (isLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
          <div className="text-sm text-gray-600">Rendering chart...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="text-red-500 text-2xl mb-3">⚠️</div>
            <div className="text-red-700 font-medium text-lg mb-2">Render Error</div>
            <div className="text-red-600 text-sm mb-4 font-mono bg-red-100 p-2 rounded">
              {error}
            </div>
            <div className="space-y-2">
              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm font-medium transition-colors"
              >
                Reload Page
              </button>
              <button
                onClick={() => {
                  setError(null)
                  setIsLoading(true)
                  // Retry rendering
                  setTimeout(() => {
                    window.location.reload()
                  }, 100)
                }}
                className="w-full px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm font-medium transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!RenderedComponent) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-3">📊</div>
          <div className="text-lg font-medium">No Chart to Display</div>
          <div className="text-sm mt-1">Component not available</div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-full overflow-auto">
      <React.Suspense fallback={
        <div className="w-full h-full flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto mb-2"></div>
            <div className="text-sm text-gray-600">Loading chart...</div>
          </div>
        </div>
      }>
        {/* Ensure the component has explicit dimensions and styles for dynamic content */}
        <div className="w-full h-full min-h-[400px]" style={{
          /* Inline styles as fallback since Tailwind might not work in dynamic components */
          width: '100%',
          height: '100%',
          minHeight: '400px'
        }}>
          <style jsx global>{`
            /* Ensure basic styles work in dynamic components */
            .w-full { width: 100% !important; }
            .h-full { height: 100% !important; }
            .flex { display: flex !important; }
            .items-center { align-items: center !important; }
            .justify-center { justify-content: center !important; }
            .text-center { text-align: center !important; }
            .text-red-500 { color: #ef4444 !important; }
            .text-red-700 { color: #b91c1c !important; }
            .text-2xl { font-size: 1.5rem !important; }
            .mb-4 { margin-bottom: 1rem !important; }
            .mb-2 { margin-bottom: 0.5rem !important; }
            .p-4 { padding: 1rem !important; }
            .max-w-2xl { max-width: 42rem !important; }
            .bg-gray-100 { background-color: #f3f4f6 !important; }
            .rounded { border-radius: 0.25rem !important; }
          `}</style>
          <RenderedComponent />
        </div>
      </React.Suspense>
    </div>
  )
}