/** @type {import('next').NextConfig} */
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development'
});

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production' 
          ? 'https://financedashboard-production-50f3.up.railway.app/api/:path*'
          : 'http://localhost:7000/api/:path*',
      },
    ];
  },
  images: {
    domains: ['localhost', 'financedashboard-production-50f3.up.railway.app'],
  },
};

module.exports = withPWA(nextConfig);