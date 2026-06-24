// src/types/address.ts
export interface Address {
  id: number;
  user_id: number;
  name: string;
  phone: string;
  province: string;
  city: string;
  district: string;
  detail: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface AddressCreate {
  name: string;
  phone: string;
  province: string;
  city: string;
  district: string;
  detail: string;
  is_default?: boolean;
}

export interface AddressUpdate {
  name?: string;
  phone?: string;
  province?: string;
  city?: string;
  district?: string;
  detail?: string;
  is_default?: boolean;
}
