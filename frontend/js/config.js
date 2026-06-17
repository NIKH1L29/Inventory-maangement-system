/**
 * API base URL config.
 * Saved in localStorage so you don't re-type it every refresh.
 * When you deploy, set DEFAULT_API_URL to your Render/Railway URL before pushing,
 * or users can paste it in the UI.
 */
const DEFAULT_API_URL = "http://localhost:8000";
const STORAGE_KEY = "inventory_api_url";

function getApiBaseUrl() {
  return localStorage.getItem(STORAGE_KEY) || DEFAULT_API_URL;
}

function setApiBaseUrl(url) {
  // Trim trailing slash - keeps fetch URLs consistent
  const cleaned = url.replace(/\/+$/, "");
  localStorage.setItem(STORAGE_KEY, cleaned);
  return cleaned;
}
