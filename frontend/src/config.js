// Configuration utility for accessing runtime configs
// This reads from window.configs which is loaded from /config.js

/**
 * Get the API base URL from runtime configuration
 * Falls back to "/" if not configured
 */
export const getApiUrl = () => {
  return window?.configs?.apiUrl ? window.configs.apiUrl : "/";
};

/**
 * Get the full API endpoint URL
 * @param {string} endpoint - The API endpoint path (e.g., '/api/health')
 * @returns {string} The full URL
 */
export const getApiEndpoint = (endpoint) => {
  const baseUrl = getApiUrl();
  // Remove trailing slash from baseUrl and leading slash from endpoint if both exist
  const cleanBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${cleanBase}${cleanEndpoint}`;
};

/**
 * Get environment from config
 */
export const getEnvironment = () => {
  return window?.configs?.environment || "development";
};

/**
 * Get version from config
 */
export const getVersion = () => {
  return window?.configs?.version || "unknown";
};

/**
 * Check if we're in production mode
 */
export const isProduction = () => {
  return getEnvironment() === "production";
};

