import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "ci.encar.com", pathname: "/**" },
      { protocol: "https", hostname: "img.encar.com", pathname: "/**" },
    ],
  },
};

export default nextConfig;
