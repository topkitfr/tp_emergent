import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Proxy external CDN images through our backend to avoid CORS/referrer issues
export const proxyImageUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('/api/uploads/')) return `${BACKEND_URL}${url}`;
  if (url.startsWith('https://cdn.footballkitarchive.com/')) {
    return `${API}/image-proxy?url=${encodeURIComponent(url)}`;
  }
  return url;
};

const api = axios.create({
  baseURL: API,
  // withCredentials: true, // désactivé pour le dev local
});

// Auth
export const createSession = (session_id) => api.post('/auth/session', { session_id });
export const getMe = () => api.get('/auth/me');
export const logout = () => api.post('/auth/logout');

// Master Kits
export const getMasterKits = (params) => api.get('/master-kits', { params });
export const getMasterKit = (kitId) => api.get(`/master-kits/${kitId}`);
export const createMasterKit = (data) => api.post('/master-kits', data);
export const getFilters = () => api.get('/master-kits/filters');
export const getMasterKitsCount = () => api.get('/master-kits/count');

// Versions
export const getVersion = (versionId) => api.get(`/versions/${versionId}`);
export const createVersion = (data) => api.post('/versions', data);
export const getVersions = (params) => api.get('/versions', { params });

// Collections
export const getMyCollection = (params) => api.get('/collections', { params });
export const getCollectionCategories = () => api.get('/collections/categories');
export const addToCollection = (data) => api.post('/collections', data);
export const removeFromCollection = (id) => api.delete(`/collections/${id}`);
export const updateCollectionItem = (id, data) => api.put(`/collections/${id}`, data);
export const getCollectionStats = () => api.get('/collections/stats');
export const getCategoryStats = () => api.get('/collections/category-stats');

// Reviews
export const createReview = (data) => api.post('/reviews', data);
export const getReviews = (versionId) => api.get('/reviews', { params: { version_id: versionId } });

// Version Estimates
export const getVersionEstimates = (versionId) => api.get(`/versions/${versionId}/estimates`);

// Stats
export const getStats = () => api.get('/stats');

// Seed
export const seedData = () => api.post('/seed');

// Upload
export const uploadImage = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
};

// User Profile
export const getUserProfile = (userId) => api.get(`/users/${userId}/profile`);
export const getUserByUsername = (username) => api.get(`/users/by-username/${username}`);
export const updateProfile = (data) => api.put('/users/profile', data);

// Submissions
export const createSubmission = (data) => api.post('/submissions', data);
export const getSubmissions = (params) => api.get('/submissions', { params });
export const getSubmission = (id) => api.get(`/submissions/${id}`);
export const voteOnSubmission = (id, vote) => api.post(`/submissions/${id}/vote`, { vote });

// Reports
export const createReport = (data) => api.post('/reports', data);
export const getReports = (params) => api.get('/reports', { params });
export const voteOnReport = (id, vote) => api.post(`/reports/${id}/vote`, { vote });

// Wishlist
export const getWishlist = () => api.get('/wishlist');
export const addToWishlist = (data) => api.post('/wishlist', data);
export const removeFromWishlist = (id) => api.delete(`/wishlist/${id}`);
export const checkWishlist = (versionId) => api.get(`/wishlist/check/${versionId}`);

// Autocomplete
export const getAutocomplete = (field, q) => api.get('/autocomplete', { params: { field, q } });
export const getEntityAutocomplete = (type, query) => api.get('/autocomplete', { params: { type, query } });

// Teams
export const getTeams = (params) => api.get('/teams', { params });
export const getTeam = (id) => api.get(`/teams/${id}`);
export const createTeam = (data) => api.post('/teams', data);
export const updateTeam = (id, data) => api.put(`/teams/${id}`, data);

// Leagues
export const getLeagues = (params) => api.get('/leagues', { params });
export const getLeague = (id) => api.get(`/leagues/${id}`);
export const createLeague = (data) => api.post('/leagues', data);
export const updateLeague = (id, data) => api.put(`/leagues/${id}`, data);

// Brands
export const getBrands = (params) => api.get('/brands', { params });
export const getBrand = (id) => api.get(`/brands/${id}`);
export const createBrand = (data) => api.post('/brands', data);
export const updateBrand = (id, data) => api.put(`/brands/${id}`, data);

// Players
export const getPlayers = (params) => api.get('/players', { params });
export const getPlayer = (id) => api.get(`/players/${id}`);
export const createPlayer = (data) => api.post('/players', data);
export const updatePlayer = (id, data) => api.put(`/players/${id}`, data);

// Migration
export const migrateEntities = () => api.post('/migrate-entities-from-kits');

export default api;
