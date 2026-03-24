// src/lib/utils.js
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

export function proxyImageUrl(url) {
  if (!url) return '';
  if (url.startsWith('/api/uploads/')) return `${BACKEND_URL}${url}`;
  if (url.startsWith('https://cdn.footballkitarchive.com/')) {
    return `${API}/image-proxy?url=${encodeURIComponent(url)}`;
  }
  return url;
}
