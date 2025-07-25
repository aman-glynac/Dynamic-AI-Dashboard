'use client'

import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'

export default function PromptInput() {
  const [prompt, setPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isApiHealthy, setIsApiHealthy] = useState<boolean | null>(null)

  // Check API health on mount
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        // Try to import api service dynamically to avoid SSR issues
        const { apiService } = await import('@/services/api')
        await apiService.healthCheck()
        setIsApiHealthy(true)
      } catch (error) {
        setIsApiHealthy(false)
        console.error('API health check failed:', error)
      }
    }

    checkApiHealth()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!prompt.trim()) {
      toast.error('Please enter a prompt')
      return
    }

    if (!isApiHealthy) {
      toast.error('API is not available. Please check the backend server.')
      return
    }

    try {
      setIsLoading(true)

      // Call the chart generation function from Canvas component
      if (typeof (window as any).generateChart === 'function') {
        await (window as any).generateChart(prompt)
        setPrompt('') // Clear prompt on success
      } else {
        throw new Error('Chart generation function not available')
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate chart'
      toast.error(errorMessage)
      console.error('Prompt submission error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="p-4 border-t border-gray-200 bg-white">
      {/* API Status Indicator */}
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            isApiHealthy === null ? 'bg-yellow-400' : 
            isApiHealthy ? 'bg-green-400' : 'bg-red-400'
          }`}></div>
          <span className="text-xs text-gray-500">
            {isApiHealthy === null ? 'Checking API...' : 
             isApiHealthy ? 'API Connected' : 'API Unavailable'}
          </span>
        </div>
        
        {!isApiHealthy && isApiHealthy !== null && (
          <button
            onClick={() => window.location.reload()}
            className="text-xs text-blue-500 hover:text-blue-700"
          >
            Retry Connection
          </button>
        )}
      </div>

      {/* Prompt Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={
            !isApiHealthy ? 'API unavailable...' : 
            isLoading ? 'Generating chart...' :
            'Enter your prompt here... (e.g., "show me sales by platform")'
          }
          disabled={isLoading || !isApiHealthy}
          className={`flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
            isLoading || !isApiHealthy ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
          }`}
        />
        <button
          type="submit"
          disabled={!prompt.trim() || isLoading || !isApiHealthy}
          className={`px-6 py-2 rounded-lg font-medium transition-all duration-200 ${
            !prompt.trim() || isLoading || !isApiHealthy
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 shadow-sm hover:shadow-md'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Generating...</span>
            </div>
          ) : (
            'Generate Chart'
          )}
        </button>
      </form>

      {/* Usage Examples */}
      {!isLoading && isApiHealthy && (
        <div className="mt-3 text-xs text-gray-500">
          <span className="font-medium">Try:</span> 
          <button 
            onClick={() => setPrompt('show me sales by platform')}
            className="ml-2 text-blue-500 hover:text-blue-700"
          >
            "show me sales by platform"
          </button>
          <span className="mx-2">•</span>
          <button 
            onClick={() => setPrompt('create a bar chart of top 10 games')}
            className="text-blue-500 hover:text-blue-700"
          >
            "create a bar chart of top 10 games"
          </button>
        </div>
      )}
    </div>
  )
}