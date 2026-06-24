// src/types/coupon.ts
export interface Coupon {
  id: number;
  code: string;
  name: string;
  description: string | null;
  type: 'fixed' | 'percent';
  value: number;
  min_amount: number;
  start_date: string;
  end_date: string;
  usage_limit: number;
  used_count: number;
  is_active: boolean;
  created_at: string;
}

export interface UserCoupon {
  id: number;
  user_id: number;
  coupon_id: number;
  is_used: boolean;
  used_at: string | null;
  order_id: number | null;
  created_at: string;
  coupon: Coupon | null;
}

export interface ClaimCouponRequest {
  code: string;
}

export interface ApplyCouponRequest {
  coupon_code: string;
  order_amount: number;
}

export interface ApplyCouponResult {
  coupon_id: number;
  code: string;
  name: string;
  type: 'fixed' | 'percent';
  value: number;
  discount_amount: number;
  final_amount: number;
}
