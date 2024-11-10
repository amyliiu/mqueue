// next.config.js
module.exports = {
    images: {
      domains: ['yourdomain.com'], // Domains allowed for Next.js Image Optimization
    },
    env: {
      API_URL: process.env.API_URL || 'http://localhost:8000', // Example environment variable
    },
  };
  