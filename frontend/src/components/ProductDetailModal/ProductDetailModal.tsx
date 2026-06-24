import { useEffect, useState } from 'react';
import { productPublicApi } from '../../api/productPublic';
import { favoritesApi } from '../../api/favorites';
import { useAuthStore } from '../../store/authStore';
import ReviewsSection from '../ReviewsSection';
import type { Product } from '../../types/product';
import styles from './ProductDetailModal.module.css';

interface ProductDetailModalProps {
  visible: boolean;
  productId: number | null;
  onClose: () => void;
}

const ProductDetailModal = ({ visible, productId, onClose }: ProductDetailModalProps) => {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favLoading, setFavLoading] = useState(false);
  const { token } = useAuthStore();

  useEffect(() => {
    if (visible && productId) {
      const fetchDetail = async () => {
        try {
          setLoading(true);
          setError(null);
          const data = await productPublicApi.getDetail(productId);
          setProduct(data);
        } catch (err) {
          console.error('获取商品详情失败:', err);
          setError('加载商品详情失败，请重试');
        } finally {
          setLoading(false);
        }
      };
      fetchDetail();
    } else {
      // 重置状态
      setProduct(null);
      setError(null);
      setIsFavorited(false);
    }
  }, [visible, productId]);

  // 检查是否已收藏
  useEffect(() => {
    if (visible && productId && token) {
      const checkFavorite = async () => {
        try {
          const result = await favoritesApi.check(productId);
          setIsFavorited(result.is_favorited);
        } catch (err) {
          console.error('检查收藏状态失败:', err);
        }
      };
      checkFavorite();
    }
  }, [visible, productId, token]);

  const handleToggleFavorite = async () => {
    if (!productId || !token) return;
    setFavLoading(true);
    try {
      if (isFavorited) {
        await favoritesApi.remove(productId);
        setIsFavorited(false);
      } else {
        await favoritesApi.add(productId);
        setIsFavorited(true);
      }
    } catch (err) {
      console.error('操作收藏失败:', err);
    } finally {
      setFavLoading(false);
    }
  };

  if (!visible) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h5 className={styles.title}>商品详情</h5>
          <button className={styles.closeBtn} onClick={onClose}>×</button>
        </div>
        <div className={styles.modalBody}>
          {loading && (
            <div className="text-center py-4">
              <div className="spinner-border text-danger" />
            </div>
          )}
          {error && <div className="alert alert-danger">{error}</div>}
          {product && !loading && !error && (
            <div className={styles.detailContainer}>
              <img
                src={product.image_url || 'https://via.placeholder.com/400x300?text=No+Image'}
                alt={product.name}
                className={styles.detailImage}
              />
              <div className="d-flex align-items-center justify-content-between">
                <h3 className={styles.productName}>{product.name}</h3>
                {token && (
                  <button
                    className={`btn btn-sm ${isFavorited ? 'btn-danger' : 'btn-outline-danger'}`}
                    onClick={handleToggleFavorite}
                    disabled={favLoading}
                    title={isFavorited ? '取消收藏' : '加入收藏'}
                  >
                    <i className={`bi ${isFavorited ? 'bi-heart-fill' : 'bi-heart'}`}></i>
                    {isFavorited ? ' 已收藏' : ' 收藏'}
                  </button>
                )}
              </div>
              <p className={styles.productDesc}>{product.description || '暂无描述'}</p>
              <div className={styles.infoRow}>
                <span className={styles.label}>价格：</span>
                <span className={styles.price}>¥{product.price.toFixed(2)}</span>
              </div>
              {/* <div className={styles.infoRow}>
                <span className={styles.label}>库存：</span>
                <span>{product.stock}</span>
              </div> */}
              <div className={styles.infoRow}>
                <span className={styles.label}>分类：</span>
                <span>{product.category || '未分类'}</span>
              </div>
              {/* <div className={styles.infoRow}>
                <span className={styles.label}>状态：</span>
                <span className={product.is_active ? styles.active : styles.inactive}>
                  {product.is_active ? '上架' : '下架'}
                </span>
              </div> */}
              <hr />
              <ReviewsSection productId={product.id} />
            </div>
          )}
        </div>
        <div className={styles.modalFooter}>
          <button className={styles.closeFooterBtn} onClick={onClose}>关闭</button>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailModal;