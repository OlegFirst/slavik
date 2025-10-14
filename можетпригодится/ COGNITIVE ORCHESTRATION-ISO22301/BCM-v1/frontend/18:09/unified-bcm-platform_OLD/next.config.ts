/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ['axios'],
  },
  async rewrites() {
    return [
      {
        source: '/api/odoo/:path*',
        destination: 'http://localhost:8069/api/:path*',
      },
      {
        source: '/api/ai/:path*',
        destination: 'http://localhost:8000/:path*',
      },
      {
        source: '/api/bia/:path*',
        destination: 'http://localhost:8082/:path*',
      },
    ]
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ]
  },
}

export default nextConfig
