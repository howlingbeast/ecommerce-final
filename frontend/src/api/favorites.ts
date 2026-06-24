// src/api/favorites.ts
import apiClient from './client';
import type { Favorite } from '../types/favorite';

interface FavoriteListResponse {
  items: Favorite[];
  total: number;
}

export const favoritesApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    apiClient.get<FavoriteListResponse>('/favorites/', { params }).then(r => r.data),

  add: (productId: number) =>
    apiClient.post(`/favorites/${productId}`).then(r => r.data),

  remove: (productId: number) =>
    apiClient.delete(`/favorites/${productId}`).then(r => r.data),

  check: (productId: number) =>
    apiClient.get<{ is_favorited: boolean }>(`/favorites/check/${productId}`).then(r => r.data),
};
