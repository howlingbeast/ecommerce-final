// src/pages/AccountPage.tsx
import { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import FavoritesPage from './FavoritesPage';
import AddressesPage from './AddressesPage';
import CouponsPage from './CouponsPage';
import styles from './AccountPage.module.css';

type TabKey = 'favorites' | 'addresses' | 'coupons';

const AccountPage = () => {
  const { user, logout } = useAuthStore();
  const [activeTab, setActiveTab] = useState<TabKey>('favorites');

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  const tabs: { key: TabKey; label: string; icon: string }[] = [
    { key: 'favorites', label: '我的收藏', icon: 'bi-heart' },
    { key: 'addresses', label: '收货地址', icon: 'bi-geo-alt' },
    { key: 'coupons', label: '我的优惠券', icon: 'bi-ticket-perforated' },
  ];

  return (
    <div className={styles.container}>
      {/* User Info Summary */}
      <div className={styles.userCard}>
        <div className="d-flex align-items-center gap-3">
          <div
            className="rounded-circle bg-danger d-flex align-items-center justify-content-center text-white"
            style={{ width: '56px', height: '56px', fontSize: '1.5rem' }}
          >
            {user?.full_name?.[0] || user?.username?.[0] || 'U'}
          </div>
          <div>
            <h5 className="mb-1 fw-bold">{user?.full_name || user?.username || '用户'}</h5>
            <p className="mb-0 text-muted" style={{ fontSize: '0.85rem' }}>
              {user?.email || ''}
            </p>
          </div>
        </div>
        <div className="d-flex gap-2">
          <a href="/orders" className="btn btn-outline-danger btn-sm">
            <i className="bi bi-box me-1"></i>我的订单
          </a>
          <button className="btn btn-outline-secondary btn-sm" onClick={handleLogout}>
            <i className="bi bi-box-arrow-right me-1"></i>退出登录
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <ul className="nav nav-tabs mb-4">
        {tabs.map((tab) => (
          <li key={tab.key} className="nav-item">
            <button
              className={`nav-link ${activeTab === tab.key ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.key)}
            >
              <i className={`bi ${tab.icon} me-1`}></i>
              {tab.label}
            </button>
          </li>
        ))}
      </ul>

      {/* Tab Content */}
      <div className={styles.tabContent}>
        {activeTab === 'favorites' && <FavoritesPage />}
        {activeTab === 'addresses' && <AddressesPage />}
        {activeTab === 'coupons' && <CouponsPage />}
      </div>
    </div>
  );
};

export default AccountPage;
