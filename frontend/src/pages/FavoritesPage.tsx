// src/pages/FavoritesPage.tsx
import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { favoritesApi } from '../api/favorites';
import { useCartStore } from '../store/cartStore';
import { useAuthStore } from '../store/authStore';
import type { Favorite } from '../types/favorite';
import styles from './FavoritesPage.module.css';
import bgVideo from '../assets/product-bg-video.mp4';

const DEFAULT_IMAGE = 'https://via.placeholder.com/300x200?text=No+Image';

const FavoritesPage = () => {
  const navigate = useNavigate();
  const { addToCart } = useCartStore();
  const { user } = useAuthStore();

  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [removingIds, setRemovingIds] = useState<Set<number>>(new Set());

  const fetchFavorites = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await favoritesApi.list();
      setFavorites(res.items);
    } catch (err) {
      console.error('获取收藏失败:', err);
      setError('加载收藏商品失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFavorites();
  }, [fetchFavorites]);

  const handleRemoveFavorite = async (productId: number) => {
    setRemovingIds(prev => new Set(prev).add(productId));
    try {
      await favoritesApi.remove(productId);
      setFavorites(prev => prev.filter(f => f.product_id !== productId));
    } catch (err: any) {
      alert(err.response?.data?.detail || '取消收藏失败，请重试');
    } finally {
      setRemovingIds(prev => {
        const next = new Set(prev);
        next.delete(productId);
        return next;
      });
    }
  };

  const handleAddToCart = async (productId: number) => {
    if (!user) {
      alert('请先登录');
      navigate('/login');
      return;
    }
    try {
      await addToCart({ product_id: productId, quantity: 1 });
      alert('已添加到购物车');
    } catch (err: any) {
      alert(err.response?.data?.detail || '添加失败，请重试');
    }
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-danger" />
      </div>
    );
  }

  if (error) {
    return <div className="alert alert-danger text-center">{error}</div>;
  }

  if (!favorites || favorites.length === 0) {
    return (
      <div className={styles.emptyContainer}>
        <i className="bi bi-heartbreak fs-1 text-muted"></i>
        <p className="mt-3 text-muted">还没有收藏商品，去逛逛吧</p>
        <a href="/" className="btn btn-danger mt-2">去逛逛</a>
      </div>
    );
  }

  return (
    <div className={styles.wrapper}>
      <video className={styles.bgVideo} autoPlay muted loop playsInline>
        <source src={bgVideo} type="video/mp4" />
      </video>
      <div className={styles.bgOverlay}></div>
      <div className={styles.container}>
      <h3 className="fw-bold mb-4">
        <i className="bi bi-heart text-danger me-2"></i>
        我的收藏 ({favorites.length})
      </h3>
      <div className="row">
        {favorites.map((fav) => {
          const product = fav.product;
          if (!product) return null;
          return (
            <div key={fav.id} className="col-md-3 mb-4">
              <div className="card h-100 shadow-sm product-card">
                <img
                  src={product.image_url || DEFAULT_IMAGE}
                  className="card-img-top"
                  alt={product.name}
                  style={{ height: '200px', objectFit: 'contain', background: 'var(--jjk-surface)' }}
                />
                <div className="card-body d-flex flex-column">
                  <h5 className="card-title fs-6">{product.name}</h5>
                  <div className="d-flex justify-content-between align-items-center mt-2">
                    <span className="text-danger fw-bold fs-5">
                      ¥{product.price.toFixed(2)}
                    </span>
                    <div className="btn-group" role="group">
                      <button
                        className="btn btn-outline-danger btn-sm"
                        onClick={() => handleAddToCart(product.id)}
                      >
                        <i className="bi bi-cart-plus"></i> 加入购物车
                      </button>
                      <button
                        className={`btn btn-sm ${removingIds.has(product.id) ? 'btn-secondary disabled' : 'btn-outline-secondary'}`}
                        onClick={() => handleRemoveFavorite(product.id)}
                        disabled={removingIds.has(product.id)}
                      >
                        {removingIds.has(product.id) ? (
                          <span className="spinner-border spinner-border-sm" />
                        ) : (
                          <i className="bi bi-heart-fill text-danger"></i>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
    </div>
  );
};

export default FavoritesPage;
