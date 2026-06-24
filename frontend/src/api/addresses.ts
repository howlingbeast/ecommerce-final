// src/api/addresses.ts
import apiClient from './client';
import type { Address, AddressCreate, AddressUpdate } from '../types/address';

export const addressesApi = {
  list: () =>
    apiClient.get<Address[]>('/addresses/').then(r => r.data),

  create: (data: AddressCreate) =>
    apiClient.post<Address>('/addresses/', data).then(r => r.data),

  update: (id: number, data: AddressUpdate) =>
    apiClient.put<Address>(`/addresses/${id}`, data).then(r => r.data),

  delete: (id: number) =>
    apiClient.delete(`/addresses/${id}`).then(r => r.data),

  setDefault: (id: number) =>
    apiClient.put<Address>(`/addresses/${id}/default`).then(r => r.data),
};
