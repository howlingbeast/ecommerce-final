// src/pages/CouponsPage.tsx
import { useEffect, useState, useCallback } from 'react';
import { couponsApi } from '../api/coupons';
import type { Coupon, UserCoupon } from '../types/coupon';
import styles from './CouponsPage.module.css';
import bgVideo from '../assets/product-bg-video.mp4';

type TabKey = 'available' | 'mine';

const getCouponTypeLabel = (type: string, value: number): string => {
  if (type === 'percent') return `${value}% 折扣`;
  return `满减 ¥${value.toFixed(2)}`;
};

const formatDate = (dateStr: string): string => {
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN');
  } catch {
    return dateStr;
  }
};

const CouponsPage = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('available');

  // Available coupons
  const [availableCoupons, setAvailableCoupons] = useState<Coupon[]>([]);
  const [availableLoading, setAvailableLoading] = useState(false);
  const [availableError, setAvailableError] = useState<string | null>(null);

  // My coupons
  const [myCoupons, setMyCoupons] = useState<UserCoupon[]>([]);
  const [myLoading, setMyLoading] = useState(false);
  const [myError, setMyError] = useState<string | null>(null);

  // Claim by code
  const [claimCode, setClaimCode] = useState('');
  const [claiming, setClaiming] = useState(false);

  // Claim individual coupon
  const [claimingIds, setClaimingIds] = useState<Set<number>>(new Set());

  const fetchAvailable = useCallback(async () => {
    try {
      setAvailableLoading(true);
      setAvailableError(null);
      const res = await couponsApi.getAvailable();
      setAvailableCoupons(res);
    } catch (err) {
      console.error('获取可领取优惠券失败:', err);
      setAvailableError('获取优惠券列表失败');
    } finally {
      setAvailableLoading(false);
    }
  }, []);

  const fetchMyCoupons = useCallback(async () => {
    try {
      setMyLoading(true);
      setMyError(null);
      const res = await couponsApi.getMine();
      setMyCoupons(res);
    } catch (err) {
      console.error('获取我的优惠券失败:', err);
      setMyError('获取我的优惠券失败');
    } finally {
      setMyLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAvailable();
  }, [fetchAvailable]);

  useEffect(() => {
    if (activeTab === 'mine') {
      fetchMyCoupons();
    }
  }, [activeTab, fetchMyCoupons]);

  const handleClaimByCode = async () => {
    const code = claimCode.trim();
    if (!code) {
      alert('请输入优惠券码');
      return;
    }
    setClaiming(true);
    try {
      await couponsApi.claim(code);
      alert('领取成功！');
      setClaimCode('');
      fetchAvailable();
    } catch (err: any) {
      alert(err.response?.data?.detail || '领取失败，请检查优惠券码');
    } finally {
      setClaiming(false);
    }
  };

  const handleClaimCoupon = async (couponId: number) => {
    const coupon = availableCoupons.find(c => c.id === couponId);
    if (!coupon) return;
    setClaimingIds(prev => new Set(prev).add(couponId));
    try {
      await couponsApi.claim(coupon.code);
      alert('领取成功！');
      fetchAvailable();
    } catch (err: any) {
      alert(err.response?.data?.detail || '领取失败，请重试');
    } finally {
      setClaimingIds(prev => {
        const next = new Set(prev);
        next.delete(couponId);
        return next;
      });
    }
  };

  return (
    <div className={styles.wrapper}>
      <video className={styles.bgVideo} autoPlay muted loop playsInline>
        <source src={bgVideo} type="video/mp4" />
      </video>
      <div className={styles.bgOverlay}></div>
      <div className={styles.container}>
      <h3 className="fw-bold mb-4">
        <i className="bi bi-ticket-perforated me-2"></i>
        优惠券
      </h3>

      {/* Claim by code input */}
      <div className={styles.claimSection}>
        <div className="input-group">
          <input
            type="text"
            className="form-control"
            placeholder="输入优惠券码领取优惠券"
            value={claimCode}
            onChange={e => setClaimCode(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleClaimByCode()}
          />
          <button
            className="btn btn-danger"
            onClick={handleClaimByCode}
            disabled={claiming}
          >
            {claiming ? (
              <span className="spinner-border spinner-border-sm" />
            ) : (
              '领取'
            )}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'available' ? 'active' : ''}`}
            onClick={() => setActiveTab('available')}
          >
            可领取
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'mine' ? 'active' : ''}`}
            onClick={() => setActiveTab('mine')}
          >
            我的优惠券
          </button>
        </li>
      </ul>

      {/* Available tab */}
      {activeTab === 'available' && (
        <>
          {availableLoading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-danger" />
            </div>
          ) : availableError ? (
            <div className="alert alert-danger text-center">{availableError}</div>
          ) : availableCoupons.length === 0 ? (
            <div className={styles.emptyState}>
              <i className="bi bi-ticket-perforated fs-1 text-muted"></i>
              <p className="mt-3 text-muted">暂无可用优惠券</p>
            </div>
          ) : (
            <div className={styles.couponGrid}>
              {availableCoupons.map((coupon) => (
                <div key={coupon.id} className={styles.couponCard}>
                  <div className={styles.couponLeft}>
                    <div className={styles.couponValue}>
                      {coupon.type === 'percent' ? `${coupon.value}%` : `¥${coupon.value.toFixed(0)}`}
                    </div>
                    <div className={styles.couponType}>
                      {getCouponTypeLabel(coupon.type, coupon.value)}
                    </div>
                  </div>
                  <div className={styles.couponRight}>
                    <div className={styles.couponName}>{coupon.name}</div>
                    {coupon.description && (
                      <div className={styles.couponDesc}>{coupon.description}</div>
                    )}
                    <div className={styles.couponMeta}>
                      有效期: {formatDate(coupon.start_date)} ~ {formatDate(coupon.end_date)}
                    </div>
                    <button
                      className="btn btn-sm btn-danger mt-2"
                      onClick={() => handleClaimCoupon(coupon.id)}
                      disabled={claimingIds.has(coupon.id)}
                    >
                      {claimingIds.has(coupon.id) ? (
                        <span className="spinner-border spinner-border-sm" />
                      ) : (
                        '领取'
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* My coupons tab */}
      {activeTab === 'mine' && (
        <>
          {myLoading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-danger" />
            </div>
          ) : myError ? (
            <div className="alert alert-danger text-center">{myError}</div>
          ) : myCoupons.length === 0 ? (
            <div className={styles.emptyState}>
              <i className="bi bi-ticket-perforated fs-1 text-muted"></i>
              <p className="mt-3 text-muted">还没有领取优惠券</p>
            </div>
          ) : (
            <div className={styles.couponGrid}>
              {myCoupons.map((uc) => {
                const coupon = uc.coupon;
                if (!coupon) return null;
                return (
                  <div
                    key={uc.id}
                    className={`${styles.couponCard} ${uc.is_used ? styles.used : ''}`}
                  >
                    <div className={styles.couponLeft}>
                      <div className={styles.couponValue}>
                        {coupon.type === 'percent' ? `${coupon.value}%` : `¥${coupon.value.toFixed(0)}`}
                      </div>
                      <div className={styles.couponType}>
                        {getCouponTypeLabel(coupon.type, coupon.value)}
                      </div>
                    </div>
                    <div className={styles.couponRight}>
                      <div className={styles.couponName}>{coupon.name}</div>
                      {coupon.description && (
                        <div className={styles.couponDesc}>{coupon.description}</div>
                      )}
                      <div className={styles.couponMeta}>
                        有效期: {formatDate(coupon.start_date)} ~ {formatDate(coupon.end_date)}
                      </div>
                      <span className={`badge mt-2 ${uc.is_used ? 'bg-secondary' : 'bg-success'}`}>
                        {uc.is_used ? '已使用' : '未使用'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
    </div>
  );
};

export default CouponsPage;
