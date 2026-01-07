// Runtime configuration for both local and Choreo deployment
// This file can be dynamically generated or replaced during deployment
(function() {
  // Detect if we're running locally or on Choreo
  const isLocalDevelopment = window.location.hostname === 'localhost' ||
                             window.location.hostname === '127.0.0.1';

  // For local development, use relative path (Vite proxy will handle it)
  // For Choreo deployment, use the full API URL
  const apiUrl = isLocalDevelopment
    ? "/"
    : "https://bfdef01f-7fc1-46ea-af69-42279e15f710-dev.e1-us-east-azure.choreoapis.dev/choreo-ai-assistant/backend-yn/v1.0";

  window.configs = {
    apiUrl: apiUrl,
    environment: isLocalDevelopment ? "development" : "production",
    version: "1.0.0"
  };

  console.log('DevChoreo Config:', window.configs);
})();

