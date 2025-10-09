/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  env: {
    API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
    WS_URL: process.env.WS_URL || 'ws://localhost:8000',
  },
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },
};

export default nextConfig;
