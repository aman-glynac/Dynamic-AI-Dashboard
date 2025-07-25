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
          
          // Transform JSX to React.createElement calls
          processedCode = transformJSX(processedCode)
          
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

        // Simple JSX to React.createElement transformer
        const transformJSX = (code: string): string => {
          // This is a basic transformer - handles simple JSX cases
          let transformed = code

          // Transform self-closing tags: <Tag prop="value" />
          transformed = transformed.replace(
            /<(\w+)([^>]*?)\s*\/>/g,
            (match, tagName, props) => {
              const propsObj = parseProps(props)
              return `React.createElement(${tagName}, ${propsObj})`
            }
          )

          // Transform opening/closing tags: <Tag prop="value">children</Tag>
          // This is a simplified approach - for complex nested JSX, we'd need a proper parser
          transformed = transformed.replace(
            /<(\w+)([^>]*?)>([\s\S]*?)<\/\1>/g,
            (match, tagName, props, children) => {
              const propsObj = parseProps(props)
              const processedChildren = children.trim() ? `, ${transformJSX(children)}` : ''
              return `React.createElement(${tagName}, ${propsObj}${processedChildren})`
            }
          )

          // Handle string literals that look like HTML tags (simple text content)
          transformed = transformed.replace(
            /React\.createElement\((\w+), ([^,]+), ([^)]+)\)/g,
            (match, tag, props, children) => {
              // If children is just a string, wrap it in quotes
              if (children && !children.includes('React.createElement') && !children.startsWith('"') && !children.startsWith("'")) {
                children = `"${children.replace(/"/g, '\\"')}"`
              }
              return `React.createElement(${tag}, ${props}, ${children})`
            }
          )

          return transformed
        }

        // Parse JSX props into an object string
        const parseProps = (propsString: string): string => {
          if (!propsString.trim()) return 'null'
          
          const props: string[] = []
          const propRegex = /(\w+)=\{([^}]+)\}|(\w+)="([^"]+)"|(\w+)='([^']+)'|(\w+)/g
          let match
          
          while ((match = propRegex.exec(propsString)) !== null) {
            if (match[1] && match[2]) {
              // {value} props
              props.push(`${match[1]}: ${match[2]}`)
            } else if (match[3] && match[4]) {
              // "string" props
              props.push(`${match[3]}: "${match[4]}"`)
            } else if (match[5] && match[6]) {
              // 'string' props
              props.push(`${match[5]}: "${match[6]}"`)
            } else if (match[7]) {
              // boolean props
              props.push(`${match[7]}: true`)
            }
          }
          
          return props.length > 0 ? `{${props.join(', ')}}` : 'null'
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