// Configuration utility for accessing runtime configs
// This reads from window.configs which is loaded from /config.js

/**
 * Get the API base URL from runtime configuration
 * Falls back to "/" if not configured
 */
export const getApiUrl = () => {
  const apiUrl = window?.configs?.apiUrl || "/";
  // Ensure trailing slash for consistency
  return apiUrl.endsWith('/') ? apiUrl : `${apiUrl}/`;
};

/**
 * Get the full API endpoint URL
 * @param {string} endpoint - The API endpoint path (e.g., '/api/health')
 * @returns {string} The full URL
 */
export const getApiEndpoint = (endpoint) => {
  const baseUrl = getApiUrl();
  // Remove leading slash from endpoint if it exists since baseUrl has trailing slash
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${baseUrl}${cleanEndpoint}`;
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

