// Environment variable validation and access
// In a real app, use @t3-oss/env-nextjs or similar for runtime validation

const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api',
  appName: process.env.NEXT_PUBLIC_APP_NAME ?? 'SmartStudy AI',
  isDev: process.env.NODE_ENV === 'development',
};

export default env;
