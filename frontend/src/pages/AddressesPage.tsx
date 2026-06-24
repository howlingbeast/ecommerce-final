// src/pages/AddressesPage.tsx
import { useEffect, useState, useCallback } from 'react';
import { addressesApi } from '../api/addresses';
import type { Address, AddressCreate, AddressUpdate } from '../types/address';
import styles from './AddressesPage.module.css';
import bgVideo from '../assets/product-bg-video.mp4';

interface AddressFormData {
  name: string;
  phone: string;
  province: string;
  city: string;
  district: string;
  detail: string;
  is_default: boolean;
}

const emptyFormData: AddressFormData = {
  name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detail: '',
  is_default: false,
};

const AddressesPage = () => {
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<AddressFormData>(emptyFormData);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  const fetchAddresses = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await addressesApi.list();
      setAddresses(data);
    } catch (err) {
      console.error('获取地址失败:', err);
      setError('加载地址失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAddresses();
  }, [fetchAddresses]);

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    if (!formData.name.trim()) errors.name = '请输入收货人姓名';
    if (!formData.phone.trim()) {
      errors.phone = '请输入手机号';
    } else if (!/^\d{11}$/.test(formData.phone.trim())) {
      errors.phone = '手机号必须为11位数字';
    }
    if (!formData.province.trim()) errors.province = '请输入省份';
    if (!formData.city.trim()) errors.city = '请输入城市';
    if (!formData.district.trim()) errors.district = '请输入区县';
    if (!formData.detail.trim()) errors.detail = '请输入详细地址';
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const openAddModal = () => {
    setEditingId(null);
    setFormData(emptyFormData);
    setFormErrors({});
    setShowModal(true);
  };

  const openEditModal = (address: Address) => {
    setEditingId(address.id);
    setFormData({
      name: address.name,
      phone: address.phone,
      province: address.province,
      city: address.city,
      district: address.district,
      detail: address.detail,
      is_default: address.is_default,
    });
    setFormErrors({});
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingId(null);
    setFormData(emptyFormData);
    setFormErrors({});
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Clear field error on change
    if (formErrors[name]) {
      setFormErrors(prev => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setSubmitting(true);
    try {
      if (editingId) {
        const updateData: AddressUpdate = { ...formData };
        await addressesApi.update(editingId, updateData);
      } else {
        const createData: AddressCreate = { ...formData };
        await addressesApi.create(createData);
      }
      await fetchAddresses();
      closeModal();
    } catch (err: any) {
      alert(err.response?.data?.detail || '保存地址失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('确定要删除该地址吗？')) return;
    try {
      await addressesApi.delete(id);
      setAddresses(prev => prev.filter(a => a.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || '删除失败，请重试');
    }
  };

  const handleSetDefault = async (id: number) => {
    try {
      await addressesApi.setDefault(id);
      setAddresses(prev =>
        prev.map(a => ({
          ...a,
          is_default: a.id === id,
        }))
      );
    } catch (err: any) {
      alert(err.response?.data?.detail || '设置默认地址失败，请重试');
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

  return (
    <div className={styles.wrapper}>
      <video className={styles.bgVideo} autoPlay muted loop playsInline>
        <source src={bgVideo} type="video/mp4" />
      </video>
      <div className={styles.bgOverlay}></div>
      <div className={styles.container}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h3 className="fw-bold mb-0">
          <i className="bi bi-geo-alt me-2"></i>
          收货地址
        </h3>
        <button className="btn btn-danger" onClick={openAddModal}>
          <i className="bi bi-plus-lg me-1"></i> 新增地址
        </button>
      </div>

      {addresses.length === 0 ? (
        <div className={styles.emptyContainer}>
          <i className="bi bi-geo-alt fs-1 text-muted"></i>
          <p className="mt-3 text-muted">暂无收货地址</p>
          <button className="btn btn-danger mt-2" onClick={openAddModal}>
            新增地址
          </button>
        </div>
      ) : (
        <div className={styles.addressList}>
          {addresses.map((address) => (
            <div key={address.id} className={styles.addressCard}>
              <div className={styles.addressInfo}>
                <div className="d-flex align-items-center gap-2">
                  <span className={styles.name}>{address.name}</span>
                  <span className={styles.phone}>{address.phone}</span>
                  {address.is_default && (
                    <span className={styles.defaultBadge}>默认</span>
                  )}
                </div>
                <div className={styles.fullAddress}>
                  {address.province} {address.city} {address.district} {address.detail}
                </div>
              </div>
              <div className={styles.addressActions}>
                {!address.is_default && (
                  <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleSetDefault(address.id)}
                  >
                    设为默认
                  </button>
                )}
                <button
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => openEditModal(address)}
                >
                    编辑
                </button>
                <button
                  className="btn btn-sm btn-outline-danger"
                  onClick={() => handleDelete(address.id)}
                >
                    删除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Address Form Modal */}
      {showModal && (
        <div className="modal d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-geo-alt me-2"></i>
                  {editingId ? '编辑地址' : '新增地址'}
                </h5>
                <button type="button" className="btn-close" onClick={closeModal}></button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <div className="row g-3">
                    <div className="col-md-6">
                      <label className="form-label">收货人 <span className="text-danger">*</span></label>
                      <input
                        type="text"
                        className={`form-control ${formErrors.name ? 'is-invalid' : ''}`}
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        placeholder="请输入收货人姓名"
                      />
                      {formErrors.name && <div className="invalid-feedback">{formErrors.name}</div>}
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">手机号 <span className="text-danger">*</span></label>
                      <input
                        type="text"
                        className={`form-control ${formErrors.phone ? 'is-invalid' : ''}`}
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        placeholder="11位手机号"
                        maxLength={11}
                      />
                      {formErrors.phone && <div className="invalid-feedback">{formErrors.phone}</div>}
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">省份 <span className="text-danger">*</span></label>
                      <input
                        type="text"
                        className={`form-control ${formErrors.province ? 'is-invalid' : ''}`}
                        name="province"
                        value={formData.province}
                        onChange={handleInputChange}
                        placeholder="省份"
                      />
                      {formErrors.province && <div className="invalid-feedback">{formErrors.province}</div>}
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">城市 <span className="text-danger">*</span></label>
                      <input
                        type="text"
                        className={`form-control ${formErrors.city ? 'is-invalid' : ''}`}
                        name="city"
                        value={formData.city}
                        onChange={handleInputChange}
                        placeholder="城市"
                      />
                      {formErrors.city && <div className="invalid-feedback">{formErrors.city}</div>}
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">区县 <span className="text-danger">*</span></label>
                      <input
                        type="text"
                        className={`form-control ${formErrors.district ? 'is-invalid' : ''}`}
                        name="district"
                        value={formData.district}
                        onChange={handleInputChange}
                        placeholder="区县"
                      />
                      {formErrors.district && <div className="invalid-feedback">{formErrors.district}</div>}
                    </div>
                    <div className="col-12">
                      <label className="form-label">详细地址 <span className="text-danger">*</span></label>
                      <input
                        type="text"
                        className={`form-control ${formErrors.detail ? 'is-invalid' : ''}`}
                        name="detail"
                        value={formData.detail}
                        onChange={handleInputChange}
                        placeholder="街道、门牌号等"
                      />
                      {formErrors.detail && <div className="invalid-feedback">{formErrors.detail}</div>}
                    </div>
                    <div className="col-12">
                      <div className="form-check">
                        <input
                          type="checkbox"
                          className="form-check-input"
                          id="isDefault"
                          name="is_default"
                          checked={formData.is_default}
                          onChange={handleInputChange}
                        />
                        <label className="form-check-label" htmlFor="isDefault">
                          设为默认地址
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={closeModal}>
                    取消
                  </button>
                  <button type="submit" className="btn btn-danger" disabled={submitting}>
                    {submitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-1" />
                        保存中...
                      </>
                    ) : (
                      '保存'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
    </div>
  );
};

export default AddressesPage;
