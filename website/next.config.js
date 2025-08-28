/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  images: {
    domains: ['reliquary.io', 'cdn.reliquary.io'],
    unoptimized: false,
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization' },
        ],
      },
    ];
  },
  async redirects() {
    return [
      {
        source: '/docs',
        destination: '/documentation',
        permanent: true,
      },
      {
        source: '/api',
        destination: '/api-reference',
        permanent: true,
      },
    ];
  },
  env: {
    SITE_URL: process.env.SITE_URL || 'https://reliquary.io',
    API_URL: process.env.API_URL || 'https://api.reliquary.io',
    DOCS_URL: process.env.DOCS_URL || 'https://docs.reliquary.io',
  },
};

module.exports = nextConfig;