// src/pages/CheckoutPage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartStore } from '../store/cartStore';
import { orderApi } from '../api/order';
import { couponsApi } from '../api/coupons';
import type { ApplyCouponResult } from '../types/coupon';
import styles from './CheckoutPage.module.css';

const DEFAULT_IMAGE = '/assets/no-image.svg';

const CheckoutPage = () => {
  const navigate = useNavigate();
  const { items, totalQuantity, fetchCart } = useCartStore();
  const [shippingAddress, setShippingAddress] = useState('');
  const [couponCode, setCouponCode] = useState('');
  const [couponResult, setCouponResult] = useState<ApplyCouponResult | null>(null);
  const [couponError, setCouponError] = useState('');
  const [applyingCoupon, setApplyingCoupon] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!items.length) {
      navigate('/');
    }
  }, [items, navigate]);

  const totalAmount = items.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
  const finalAmount = couponResult ? couponResult.final_amount : totalAmount;

  const handleApplyCoupon = async () => {
    if (!couponCode.trim()) return;
    setApplyingCoupon(true);
    setCouponError('');
    setCouponResult(null);
    try {
      const result = await couponsApi.apply({
        coupon_code: couponCode.trim(),
        order_amount: totalAmount
      });
      setCouponResult(result);
    } catch (err: any) {
      setCouponError(err.response?.data?.detail || '优惠券无效');
    } finally {
      setApplyingCoupon(false);
    }
  };

  const handleRemoveCoupon = () => {
    setCouponCode('');
    setCouponResult(null);
    setCouponError('');
  };

  const handleSubmitOrder = async () => {
    if (!shippingAddress.trim()) {
      setError('请填写收货地址');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await orderApi.create({
        shipping_address: shippingAddress,
        coupon_code: couponResult?.code || undefined
      });
      await fetchCart();
      alert('订单已提交！' + (couponResult ? ` 使用优惠券「${couponResult.name}」节省 ¥${couponResult.discount_amount.toFixed(2)}` : ''));
      navigate('/orders');
    } catch (err: any) {
      setError(err.response?.data?.detail || '创建订单失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  if (!items.length) {
    return null;
  }

  return (
    <div className={styles.container}>
      <h3 className="fw-bold mb-4">确认订单</h3>
      <div className="row">
        <div className="col-md-8">
          <div className="card mb-4">
            <div className="card-header fw-bold">商品清单</div>
            <div className="card-body p-0">
              <div className="list-group list-group-flush">
                {items.map((item) => (
                  <div key={item.id} className="list-group-item">
                    <div className="d-flex gap-3">
                      <img
                        src={item.product.image_url || DEFAULT_IMAGE}
                        alt={item.product.name}
                        style={{ width: '80px', height: '80px', objectFit: 'contain' }}
                      />
                      <div className="flex-grow-1">
                        <h6 className="mb-1">{item.product.name}</h6>
                        <div className="small">单价：¥{item.product.price.toFixed(2)}</div>
                        <div>数量：{item.quantity}</div>
                      </div>
                      <div className="text-danger fw-bold">¥{(item.product.price * item.quantity).toFixed(2)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          {/* 优惠券 */}
          <div className="card mb-4">
            <div className="card-header fw-bold">
              <i className="bi bi-ticket-perforated me-1"></i>使用优惠券
            </div>
            <div className="card-body">
              <div className="input-group mb-2">
                <input
                  type="text"
                  className="form-control"
                  placeholder="输入优惠券码"
                  value={couponCode}
                  onChange={e => setCouponCode(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleApplyCoupon()}
                  disabled={!!couponResult}
                />
                {couponResult ? (
                  <button className="btn btn-outline-secondary" onClick={handleRemoveCoupon}>
                    取消
                  </button>
                ) : (
                  <button
                    className="btn btn-danger"
                    onClick={handleApplyCoupon}
                    disabled={applyingCoupon || !couponCode.trim()}
                  >
                    {applyingCoupon ? (
                      <span className="spinner-border spinner-border-sm" />
                    ) : '使用'}
                  </button>
                )}
              </div>
              {couponError && <div className="small text-danger">{couponError}</div>}
              {couponResult && (
                <div className="small text-success">
                  ✅ {couponResult.name}：已减 ¥{couponResult.discount_amount.toFixed(2)}
                </div>
              )}
            </div>
          </div>

          {/* 订单信息 */}
          <div className="card mb-4">
            <div className="card-header fw-bold">订单信息</div>
            <div className="card-body">
              <div className="d-flex justify-content-between mb-2">
                <span>商品总数：</span>
                <span>{totalQuantity} 件</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>商品金额：</span>
                <span>¥{totalAmount.toFixed(2)}</span>
              </div>
              {couponResult && (
                <div className="d-flex justify-content-between mb-2 text-success">
                  <span>优惠减免：</span>
                  <span>- ¥{couponResult.discount_amount.toFixed(2)}</span>
                </div>
              )}
              <hr />
              <div className="d-flex justify-content-between mb-3">
                <span className="fw-bold">应付金额：</span>
                <span className={`fs-5 fw-bold ${couponResult ? 'text-success' : 'text-danger'}`}>
                  ¥{finalAmount.toFixed(2)}
                </span>
              </div>
              <hr />
              <div className="mb-3">
                <label className="form-label fw-bold">收货地址</label>
                <textarea
                  className="form-control"
                  rows={3}
                  placeholder="请填写详细收货地址（省市区+街道门牌）"
                  value={shippingAddress}
                  onChange={(e) => setShippingAddress(e.target.value)}
                  required
                />
              </div>
              {error && <div className="alert alert-danger py-2">{error}</div>}
              <button
                className="btn btn-danger w-100 py-2"
                onClick={handleSubmitOrder}
                disabled={submitting}
              >
                {submitting ? '提交中...' : `提交订单 ¥${finalAmount.toFixed(2)}`}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
