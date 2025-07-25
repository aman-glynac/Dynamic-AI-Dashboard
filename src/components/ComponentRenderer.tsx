'use client'

import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'

interface ComponentRendererProps {
  componentCode: string
  componentName: string
}

export default function ComponentRenderer({ componentCode, componentName }: ComponentRendererProps) {
  const [RenderedComponent, setRenderedComponent] = useState<React.ComponentType | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const renderComponent = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // Create a safe execution context
        const safeExecute = (code: string) => {
          // Import React and Recharts
          const React = require('react')
          const recharts = require('recharts')
          
          // Remove import statements and replace with direct assignments
          let processedCode = code
            .replace(/import\s+React\s+from\s+['"]react['"];?\s*/g, '')
            .replace(/import\s+\{[^}]+\}\s+from\s+['"]recharts['"];?\s*/g, '')
            .replace(/import\s+[^;]+;?\s*/g, '') // Remove any other imports
          
          // Create a module-like environment
          const module = { exports: {} }
          const exports = module.exports

          // Wrap the component code to make it executable
          const wrappedCode = `
            // Make React and Recharts available globally
            const { ${Object.keys(recharts).join(', ')} } = arguments[3];
            
            ${processedCode}
            
            // Return the default export
            return (typeof module !== 'undefined' && module.exports && module.exports.default) || 
                   (typeof exports !== 'undefined' && exports.default) ||
                   ${componentName};
          `

          // Create a function that returns the component
          const componentFactory = new Function('React', 'module', 'exports', 'recharts', wrappedCode)
          
          // Execute with proper context
          return componentFactory(React, module, exports, recharts)
        }

        // Execute the component code safely
        const Component = safeExecute(componentCode)

        if (typeof Component === 'function') {
          setRenderedComponent(() => Component)
        } else {
          throw new Error('Generated code did not return a valid React component')
        }

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to render component'
        console.error('Component rendering error:', err)
        setError(errorMessage)
        toast.error(`Failed to render chart: ${errorMessage}`)
      } finally {
        setIsLoading(false)
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
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center p-4 border border-red-200 rounded-lg bg-red-50">
          <div className="text-red-500 text-lg mb-2">⚠️ Render Error</div>
          <div className="text-red-600 text-sm mb-3">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
          >
            Reload Page
          </button>
        </div>
      </div>
    )
  }

  if (!RenderedComponent) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center text-gray-500">
          <div className="text-lg mb-2">📊</div>
          <div className="text-sm">No chart component to render</div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-full">
      <React.Suspense fallback={
        <div className="w-full h-full flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
        </div>
      }>
        <RenderedComponent />
      </React.Suspense>
    </div>
  )
}