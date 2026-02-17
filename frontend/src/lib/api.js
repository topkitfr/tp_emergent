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

// User Profile
export const getUserProfile = (userId) => api.get(`/users/${userId}/profile`);
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

export default api;
