// src/api/coupons.ts
import apiClient from './client';
import type { UserCoupon, ApplyCouponRequest, ApplyCouponResult, Coupon } from '../types/coupon';

export const couponsApi = {
  getAvailable: (params?: { skip?: number; limit?: number }) =>
    apiClient.get<Coupon[]>('/coupons/available', { params }).then(r => r.data),

  getMine: (params?: { skip?: number; limit?: number }) =>
    apiClient.get<UserCoupon[]>('/coupons/mine', { params }).then(r => r.data),

  claim: (code: string) =>
    apiClient.post<UserCoupon>('/coupons/claim', { code }).then(r => r.data),

  apply: (data: ApplyCouponRequest) =>
    apiClient.post<ApplyCouponResult>('/coupons/apply', data).then(r => r.data),
};
