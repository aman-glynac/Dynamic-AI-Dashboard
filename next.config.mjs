/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable experimental features for dynamic component rendering
  experimental: {
    // Allow dynamic imports and eval for component rendering
    esmExternals: false,
  },
  
  // Webpack configuration for external libraries
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Make sure recharts can be dynamically imported
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        os: false,
      }
    }
    return config
  },
}

export default nextConfig