/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
  basePath: process.env.NODE_ENV === 'production' ? '/docs-website' : '',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/docs-website/' : '',
}

module.exports = nextConfig
