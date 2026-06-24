// src/api/logistics.ts
import apiClient from './client';
import type { Logistics } from '../types/logistics';

export const logisticsApi = {
  getByOrder: (orderId: number) =>
    apiClient.get<Logistics>(`/logistics/order/${orderId}`).then(r => r.data),

  simulateCreate: (orderId: number, data?: { tracking_number?: string; carrier?: string }) =>
    apiClient.post<Logistics>(`/logistics/order/${orderId}/simulate`, data || {}).then(r => r.data),

  advance: (orderId: number) =>
    apiClient.post<Logistics>(`/logistics/order/${orderId}/advance`).then(r => r.data),
};
