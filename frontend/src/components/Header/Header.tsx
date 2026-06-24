// src/components/Header/Header.tsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useCartStore } from '../../store/cartStore';
import CartDrawer from '../CartDrawer/CartDrawer';
import styles from './Header.module.css';

const Header = () => {
  const { user, logout } = useAuthStore();
  const { totalQuantity, fetchCart } = useCartStore();
  const [cartDrawerOpen, setCartDrawerOpen] = useState(false);

  const handleCartClick = () => {
    fetchCart();  // 打开时刷新购物车
    setCartDrawerOpen(true);
  };

  return (
    <>
      <header className={`${styles.header} py-2`}>
        <div className="container d-flex justify-content-between align-items-center">
          <Link to="/" className={styles.logo}>
            <span className={styles.logoIcon}>🔮</span>
            <span>NEXUS</span>
          </Link>
          <div className="d-flex align-items-center gap-2">
            {/* 购物车图标 */}
            <button className="btn btn-light btn-sm position-relative" onClick={handleCartClick}>
              <i className="bi bi-cart"></i> 购物车
              {totalQuantity > 0 && (
                <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                  {totalQuantity}
                </span>
              )}
            </button>
            {/* 收藏夹图标 */}
            <Link to="/account" className="btn btn-light btn-sm position-relative" title="我的收藏">
              <i className="bi bi-heart"></i> 收藏
            </Link>
            <Link to="/orders" className="btn btn-light btn-sm">
              我的订单
            </Link>
            {user ? (
              <>
                <span className="text-muted" style={{fontSize:'0.85rem'}}>
                  {user.full_name || user.username}
                  {user.is_superuser && (
                      <Link to="/admin" className="badge bg-primary ms-2 text-decoration-none">
                      管理
                      </Link>
                  )}
                </span>
                <button className="btn btn-light btn-sm" onClick={logout}>
                  退出
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-light btn-sm">登录</Link>
                <Link to="/register" className="btn btn-primary btn-sm">注册</Link>
              </>
            )}
          </div>
        </div>
      </header>
      <CartDrawer isOpen={cartDrawerOpen} onClose={() => setCartDrawerOpen(false)} />
    </>
  );
};

export default Header;