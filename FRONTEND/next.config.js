/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://financedashboard-production-50f3.up.railway.app/api/:path*",
      },
    ];
  },
  images: {
    domains: ['financedashboard-production-50f3.up.railway.app'],
  },
};

module.exports = nextConfig;