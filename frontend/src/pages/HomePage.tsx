// src/pages/HomePage.tsx
import { useEffect, useState } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { productPublicApi } from '../api/productPublic';
import { useCartStore } from '../store/cartStore';
import { useAuthStore } from '../store/authStore';
import type { Product } from '../types/product';
import type { CategoryContextType } from '../layouts/PublicLayout';
import ProductDetailModal from '../components/ProductDetailModal/ProductDetailModal';
import styles from './HomePage.module.css';

const DEFAULT_IMAGE = 'https://via.placeholder.com/400x300?text=No+Image';

const HomePage = () => {
  const navigate = useNavigate();
  const { activeCategory } = useOutletContext<CategoryContextType>();
  const { addToCart } = useCartStore();
  const { user } = useAuthStore();

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    const fetchHotProducts = async () => {
      try {
        setLoading(true);
        setError(null);
        const params: any = { page: 1, size: 12, is_active: true };
        if (activeCategory) params.category = activeCategory;
        const res = await productPublicApi.list(params);
        setProducts(res.items);
      } catch (err) {
        console.error('获取商品失败:', err);
        setError('加载商品失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };
    fetchHotProducts();
  }, [activeCategory]);

  const handleShowDetail = (productId: number) => {
    setSelectedProductId(productId);
    setModalVisible(true);
  };

  const handleCloseModal = () => {
    setModalVisible(false);
    setSelectedProductId(null);
  };

  const handleAddToCart = async (e: React.MouseEvent, productId: number) => {
    e.stopPropagation();
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
      <div className={styles.loadingContainer}>
        <div className="spinner-border" role="status" />
        <p className="mt-3">加载中…</p>
      </div>
    );
  }

  if (error) {
    return <div className="alert alert-danger text-center mx-3">{error}</div>;
  }

  if (products.length === 0) {
    return <div className={styles.emptyContainer}>暂无商品</div>;
  }

  return (
    <div className={styles.home}>
      <div className={styles.sectionHeader}>
        <h2 className={styles.sectionTitle}>热销推荐</h2>
        <p className={styles.sectionSubtitle}>精选好物，品质之选</p>
      </div>

      <div className={styles.productGrid} data-product-section>
        {products.map((product) => (
          <div
            key={product.id}
            className={styles.productCard}
            onClick={() => handleShowDetail(product.id)}
          >
            <img
              src={product.image_url || DEFAULT_IMAGE}
              className={styles.productImage}
              alt={product.name}
            />
            <div className={styles.productInfo}>
              <div className={styles.productName}>{product.name}</div>
              <div className={styles.productPrice}>
                ¥{product.price.toFixed(2)}
              </div>
              <button
                className={styles.addToCartBtn}
                onClick={(e) => handleAddToCart(e, product.id)}
              >
                加入购物车 →
              </button>
            </div>
          </div>
        ))}
      </div>

      <ProductDetailModal
        visible={modalVisible}
        productId={selectedProductId}
        onClose={handleCloseModal}
      />
    </div>
  );
};

export default HomePage;
