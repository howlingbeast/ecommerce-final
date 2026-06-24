// src/api/reviews.ts
import apiClient from './client';
import type { Review, ReviewCreate, ReviewStats } from '../types/review';

export const reviewsApi = {
  getProductReviews: (productId: number, params?: { skip?: number; limit?: number }) =>
    apiClient.get<Review[]>(`/reviews/product/${productId}`, { params }).then(r => r.data),

  getProductStats: (productId: number) =>
    apiClient.get<ReviewStats>(`/reviews/product/${productId}/stats`).then(r => r.data),

  create: (data: ReviewCreate) =>
    apiClient.post<Review>('/reviews/', data).then(r => r.data),

  update: (reviewId: number, data: { rating?: number; content?: string }) =>
    apiClient.put<Review>(`/reviews/${reviewId}`, data).then(r => r.data),

  delete: (reviewId: number) =>
    apiClient.delete(`/reviews/${reviewId}`).then(r => r.data),
};
