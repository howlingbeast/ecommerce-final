// src/types/favorite.ts
export interface Favorite {
  id: number;
  user_id: number;
  product_id: number;
  created_at: string;
  product?: {
    id: number;
    name: string;
    price: number;
    image_url: string | null;
    category: string | null;
    is_active: boolean;
  };
}

export interface FavoriteListResponse {
  items: Favorite[];
  total: number;
}
