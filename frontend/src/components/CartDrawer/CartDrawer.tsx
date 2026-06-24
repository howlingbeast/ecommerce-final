// src/components/CartDrawer/CartDrawer.tsx
import { useEffect } from 'react';
import { useCartStore } from '../../store/cartStore';
import styles from './CartDrawer.module.css';
import { useNavigate } from 'react-router-dom';

interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const CartDrawer = ({ isOpen, onClose }: CartDrawerProps) => {
  const { items, totalQuantity, isLoading, fetchCart, updateItemQuantity, removeItem, clearCart } = useCartStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen) {
      fetchCart();
    }
  }, [isOpen, fetchCart]);

  const handleQuantityChange = async (itemId: number, currentQty: number, delta: number) => {
    const newQty = currentQty + delta;
    if (newQty < 1) return;
    await updateItemQuantity(itemId, newQty);
  };

  const handleRemove = async (itemId: number) => {
    if (window.confirm('确定要从购物车移除该商品吗？')) {
      await removeItem(itemId);
    }
  };

  const handleClear = async () => {
    if (window.confirm('确定清空购物车吗？')) {
      await clearCart();
    }
  };

  const handleCheckout = () => {
    onClose();
    navigate('/checkout');
  };

  return (
    <>
      {isOpen && <div className={`${styles.overlay} ${isOpen ? styles.overlayOpen : ''}`} onClick={onClose} />}
      <div className={`${styles.drawer} ${isOpen ? styles.drawerOpen : ''}`}>
        <div className={styles.header}>
          <h5>🛒 购物车</h5>
          <button className={styles.closeBtn} onClick={onClose}>×</button>
        </div>
        <div className={styles.body}>
          {isLoading && <div className="text-center py-4"><div className="spinner-border" /></div>}
          {!isLoading && items.length === 0 && (
            <div className={styles.emptyCart}>
              <i className="bi bi-cart"></i>
              <p>购物车空空如也~</p>
            </div>
          )}
          {items.map((item) => (
            <div key={item.id} className={styles.item}>
              <img
                src={item.product?.image_url || 'https://via.placeholder.com/80'}
                alt={item.product?.name || '商品'}
                className={styles.itemImage}
              />
              <div className={styles.itemInfo}>
                <div className={styles.itemName}>{item.product?.name || '商品'}</div>
                <div className={styles.itemBottom}>
                  <span className={styles.itemPrice}>¥{item.product?.price?.toFixed?.(2) || '0.00'}</span>
                  <div className="d-flex align-items-center gap-1">
                    <button className={styles.quantityBtn} onClick={() => handleQuantityChange(item.id, item.quantity, -1)}>-</button>
                    <span className="px-1">{item.quantity}</span>
                    <button className={styles.quantityBtn} onClick={() => handleQuantityChange(item.id, item.quantity, 1)}>+</button>
                  </div>
                </div>
                <button className="btn btn-sm btn-outline-danger mt-1" onClick={() => handleRemove(item.id)}>删除</button>
              </div>
            </div>
          ))}
        </div>
        <div className={styles.footer}>
          <div className={styles.totalRow}>
            <span className={styles.totalLabel}>合计</span>
            <span className={styles.totalPrice}>
              ¥{items.reduce((sum, i) => sum + (i.product?.price || 0) * i.quantity, 0).toFixed(2)}
            </span>
          </div>
          <div className="d-flex gap-2">
            {items.length > 0 && (
              <button className="btn btn-outline-danger btn-sm flex-fill" onClick={handleClear}>清空</button>
            )}
            <button className="btn btn-danger btn-sm flex-fill" onClick={handleCheckout}>去结算</button>
          </div>
        </div>
      </div>
    </>
  );
};

export default CartDrawer;
