// Automatically detect if we are on the same domain as the backend or if we need the hardcoded URL
const currentOrigin = window.location.origin;
const API_BASE_URL = currentOrigin.includes('localhost') || currentOrigin.includes('127.0.0.1')
    ? "http://localhost:8000/api"
    : `${currentOrigin}/api`;

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_BASE_URL };
}
