// src/types/review.ts
export interface Review {
  id: number;
  product_id: number;
  user_id: number;
  order_id: number | null;
  rating: number;
  content: string | null;
  created_at: string;
  user?: {
    id: number;
    username: string;
    full_name: string | null;
  };
}

export interface ReviewCreate {
  product_id: number;
  rating: number;
  content?: string;
  order_id?: number;
}

export interface ReviewStats {
  total_reviews: number;
  avg_rating: number;
  rating_distribution: Record<number, number>;
}

export interface ReviewListResponse {
  items: Review[];
  total: number;
}
