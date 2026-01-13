/** @type {import('next').NextConfig} */
module.exports = {
  distDir: process.env.NODE_ENV === 'production' ? '../dist' : '.next',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  webpack: config => {
    return config
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}
