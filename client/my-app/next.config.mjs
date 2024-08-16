const nextConfig = {
    async rewrites() {
      return [
        {
            source: '/:path*',
            destination: 'http://server:5000/:path*',
        },
      ];
    }
  };
  
  export default nextConfig;