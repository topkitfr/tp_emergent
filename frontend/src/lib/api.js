import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API,
  withCredentials: true,
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

// Reviews
export const createReview = (data) => api.post('/reviews', data);
export const getReviews = (versionId) => api.get('/reviews', { params: { version_id: versionId } });

// Stats
export const getStats = () => api.get('/stats');

// Seed
export const seedData = () => api.post('/seed');

// User Profile
export const getUserProfile = (userId) => api.get(`/users/${userId}/profile`);

export default api;
