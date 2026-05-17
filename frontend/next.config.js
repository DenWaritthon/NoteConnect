function normalizeBasePath(value) {
  if (!value) {
    return "";
  }

  const normalized = value.startsWith("/") ? value : `/${value}`;
  return normalized.replace(/\/+$/, "");
}

const basePath = normalizeBasePath(process.env.NEXT_PUBLIC_APP_BASE_PATH);

const nextConfig = {
  webpack(config) {
    config.module.rules.push({
      test: /\.svg$/,
      use: ["@svgr/webpack"],
    });
    return config;
  },
  basePath,
  env: {
    NEXT_PUBLIC_APP_BASE_PATH: basePath,
  },
  output: "standalone",
};

module.exports = nextConfig;
