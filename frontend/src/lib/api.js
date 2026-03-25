// frontend/src/lib/api.js
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const proxyImageUrl = (url) => {
  if (!url) return '';
  // Images NAS Freebox via proxy backend (deux préfixes possibles)
  if (url.startsWith('/api/uploads/') || url.startsWith('/api/images/')) {
    return `${BACKEND_URL}${url}`;
  }
  // Images CDN externes : chargées directement
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  return url;
};

const api = axios.create({
  baseURL: API,
  withCredentials: true,
  timeout: 15000,
});

// ─── Intercepteur de réponse — gestion globale des erreurs ──────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers?.['retry-after'];
      error.message = `Trop de requêtes. Réessayez dans ${retryAfter || 60} secondes.`;
    }
    if (
      error.response?.status === 401 &&
      !error.config?.url?.includes('/auth/me') &&
      !error.config?.url?.includes('/auth/login')
    ) {}
    return Promise.reject(error);
  }
);

export const getVersionWornBy = (versionId) => api.get(`/versions/${versionId}/worn-by`);
export const getReviews = (versionId) => api.get(`/reviews`, { params: { version_id: versionId } });

// Auth
export const loginUser = (email, password) => api.post('/auth/login', { email, password });
export const registerUser = (email, password, name) => api.post('/auth/register', { email, password, name });
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

// Version Estimates
export const getVersionEstimates = (versionId) => api.get(`/versions/${versionId}/estimates`);

// Stats
export const getStats = () => api.get('/stats');

// Seed
export const seedData = () => api.post('/seed');

// Upload
export const uploadImage = (file, folder = 'master_kit') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('folder', folder);
  return api.post('/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
};

// User Profile
export const getUserProfile     = (userId)   => api.get(`/users/${userId}/profile`);
export const getUserByUsername  = (username) => api.get(`/users/by-username/${username}`);
export const updateProfile      = (data)     => api.put('/users/profile', data);
export const updateCredentials  = (data)     => api.put('/users/credentials', data);
export const getUserBadges      = ()         => api.get('/users/profile/badges');
export const followEntity       = (data)     => api.post('/users/follow', data);
export const unfollowEntity     = (data)     => api.delete('/users/follow', { data });
export const getFollows         = ()         => api.get('/users/follows');
export const isFollowing        = (type, id) => api.get(`/users/follows/${type}/${id}`);
export const votePlayerAura     = (playerId, score) => api.post(`/players/${playerId}/aura`, { score });
export const getPlayerAura      = (playerId) => api.get(`/players/${playerId}/aura`);

// ── Listes personnalisées ──────────────────────────────────────────
export const getUserLists       = ()                      => api.get('/lists');
export const getListDetail      = (listId)                => api.get(`/lists/${listId}`);
export const createList         = (data)                  => api.post('/lists', data);
export const updateList         = (listId, data)          => api.patch(`/lists/${listId}`, data);
export const deleteList         = (listId)                => api.delete(`/lists/${listId}`);
export const addItemToList      = (listId, collectionId)  => api.post(`/lists/${listId}/items`, { collection_id: collectionId });
export const removeItemFromList = (listId, collectionId)  => api.delete(`/lists/${listId}/items/${collectionId}`);

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
export const getEntityAutocomplete = (type, query) =>
  api.get('/autocomplete', { params: { type, query } });

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

// Sponsors
export const getSponsors    = (params) => api.get('/sponsors', { params });
export const getSponsor     = (id)     => api.get(`/sponsors/${id}`);
export const getSponsorKits = (slug)   => api.get(`/sponsors/${slug}/kits`);

// Players
export const getPlayers    = (params) => api.get('/players', { params });
export const getPlayer     = (id)     => api.get(`/players/${id}`);
export const getPlayerKits = (slug)   => api.get(`/players/${slug}/kits`);
export const createPlayer  = (data)   => api.post('/players', data);
export const updatePlayer  = (id, data) => api.put(`/players/${id}`, data);

// Migration
export const migrateEntities = () => api.post('/migrate-entities-from-kits');

// Pending entities
export const createTeamPending = (data, parentSubmissionId = null) =>
  api.post('/teams/pending', data, {
    params: parentSubmissionId ? { parent_submission_id: parentSubmissionId } : {},
  });

export const createBrandPending = (data, parentSubmissionId = null) =>
  api.post('/brands/pending', data, {
    params: parentSubmissionId ? { parent_submission_id: parentSubmissionId } : {},
  });

export const createLeaguePending = (data, parentSubmissionId = null) =>
  api.post('/leagues/pending', data, {
    params: parentSubmissionId ? { parent_submission_id: parentSubmissionId } : {},
  });

export const createPlayerPending = (data, parentSubmissionId = null) =>
  api.post('/players/pending', data, {
    params: parentSubmissionId ? { parent_submission_id: parentSubmissionId } : {},
  });

export const createSponsorPending = (data, parentSubmissionId = null) =>
  api.post('/sponsors/pending', data, {
    params: parentSubmissionId ? { parent_submission_id: parentSubmissionId } : {},
  });

// Players who wore this kit
export const getKitPlayers = (kitId) => api.get(`/kits/${kitId}/players`);

// Notifications
export const getNotifications = () => api.get('/notifications');
export const markNotificationRead = (id) => api.patch(`/notifications/${id}/read`);
export const markAllNotificationsRead = () => api.patch('/notifications/read-all');
export const deleteNotification = (id) => api.delete(`/notifications/${id}`);

export default api;
