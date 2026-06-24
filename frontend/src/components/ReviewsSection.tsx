// src/components/ReviewsSection.tsx
import { useEffect, useState } from 'react';
import { reviewsApi } from '../api/reviews';
import type { Review, ReviewStats } from '../types/review';

interface ReviewsSectionProps {
  productId: number;
}

const renderStars = (rating: number) => {
  const stars: React.ReactNode[] = [];
  for (let i = 1; i <= 5; i++) {
    if (i <= rating) {
      stars.push(<i key={i} className="bi bi-star-fill text-warning me-1"></i>);
    } else if (i - 0.5 <= rating) {
      stars.push(<i key={i} className="bi bi-star-half text-warning me-1"></i>);
    } else {
      stars.push(<i key={i} className="bi bi-star text-warning me-1"></i>);
    }
  }
  return stars;
};

const ReviewsSection = ({ productId }: ReviewsSectionProps) => {
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [statsData, reviewsData] = await Promise.all([
          reviewsApi.getProductStats(productId),
          reviewsApi.getProductReviews(productId, { skip: 0, limit: 10 }),
        ]);
        setStats(statsData);
        setReviews(reviewsData);
      } catch (err) {
        console.error('获取评价失败:', err);
        setError('加载评价失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [productId]);

  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="spinner-border text-danger" />
      </div>
    );
  }

  if (error) {
    return <div className="alert alert-danger text-center">{error}</div>;
  }

  if (!stats || stats.total_reviews === 0) {
    return (
      <div className="text-center py-4">
        <i className="bi bi-chat-dots fs-1 text-muted"></i>
        <p className="mt-2 text-muted">暂无评价</p>
      </div>
    );
  }

  // Rating distribution from 5 to 1
  const ratingLevels = [5, 4, 3, 2, 1];

  return (
    <div>
      {/* Stats header */}
      <div className="d-flex align-items-center gap-4 mb-4 p-3 bg-light rounded-3">
        <div className="text-center">
          <div className="display-4 fw-bold text-danger">
            {stats.avg_rating.toFixed(1)}
          </div>
          <div className="d-flex justify-content-center">
            {renderStars(Math.round(stats.avg_rating))}
          </div>
          <small className="text-muted">{stats.total_reviews} 条评价</small>
        </div>
        <div className="flex-grow-1">
          {ratingLevels.map((level) => {
            const count = stats.rating_distribution[level] || 0;
            const percentage = stats.total_reviews > 0
              ? (count / stats.total_reviews) * 100
              : 0;
            return (
              <div key={level} className="d-flex align-items-center gap-2 mb-1">
                <span style={{ width: '30px', fontSize: '0.85rem' }}>{level}星</span>
                <div className="progress flex-grow-1" style={{ height: '8px' }}>
                  <div
                    className="progress-bar bg-warning"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span style={{ width: '30px', fontSize: '0.8rem', color: 'var(--jjk-text-dim)' }}>
                  {count}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Reviews list */}
      <div className="d-flex flex-column gap-3">
        {reviews.map((review) => (
          <div key={review.id} className="border-bottom pb-3">
            <div className="d-flex align-items-center gap-2 mb-1">
              <div
                className="rounded-circle bg-secondary d-flex align-items-center justify-content-center text-white"
                style={{ width: '32px', height: '32px', fontSize: '0.8rem' }}
              >
                {review.user?.full_name?.[0] || review.user?.username?.[0] || '?'}
              </div>
              <div>
                <span className="fw-semibold" style={{ fontSize: '0.9rem' }}>
                  {review.user?.full_name || review.user?.username || '匿名用户'}
                </span>
                <div className="d-flex align-items-center">
                  {renderStars(review.rating)}
                  <span className="text-muted ms-2" style={{ fontSize: '0.8rem' }}>
                    {new Date(review.created_at).toLocaleDateString('zh-CN')}
                  </span>
                </div>
              </div>
            </div>
            {review.content && (
              <p className="mb-0 mt-1" style={{ fontSize: '0.9rem', color: 'var(--jjk-text-dim)' }}>
                {review.content}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReviewsSection;
