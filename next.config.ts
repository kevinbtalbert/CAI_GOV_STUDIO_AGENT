import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,

  // For now, remove or omit the `webpack` override,
  // so Turbopack doesn't complain in dev mode:
  // webpack(config, options) {
  //   // (Removed custom chunk-splitting)
  //   return config;
  // },

  experimental: {
    turbo: {
      // (Optional) Place any Turbopack-specific config here in the future
    },
  },
};

export default nextConfig;
