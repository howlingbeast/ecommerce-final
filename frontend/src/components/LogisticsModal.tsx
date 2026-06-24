// src/components/LogisticsModal.tsx
import { useEffect, useState } from 'react';
import { logisticsApi } from '../api/logistics';
import { LogisticsStatusText, LogisticsStatusColor } from '../types/logistics';
import type { Logistics } from '../types/logistics';

interface LogisticsModalProps {
  visible: boolean;
  orderId: number | null;
  onClose: () => void;
}

const LogisticsModal = ({ visible, orderId, onClose }: LogisticsModalProps) => {
  const [logistics, setLogistics] = useState<Logistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (visible && orderId) {
      const fetchLogistics = async () => {
        try {
          setLoading(true);
          setError(null);
          const data = await logisticsApi.getByOrder(orderId);
          setLogistics(data);
        } catch (err: any) {
          console.error('获取物流信息失败:', err);
          if (err.response?.status === 404) {
            setError('暂无物流信息');
          } else {
            setError('获取物流信息失败，请稍后重试');
          }
        } finally {
          setLoading(false);
        }
      };
      fetchLogistics();
    }
  }, [visible, orderId]);

  if (!visible) return null;

  const statusColor = logistics ? LogisticsStatusColor[logistics.status] || '#6c757d' : '#6c757d';
  const statusText = logistics ? LogisticsStatusText[logistics.status] || logistics.status : '';

  return (
    <div className="modal d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-dialog-centered modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">
              <i className="bi bi-truck me-2"></i>
              物流追踪
            </h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            {loading ? (
              <div className="text-center py-4">
                <div className="spinner-border text-danger" />
              </div>
            ) : error ? (
              <div className="text-center py-4">
                <i className="bi bi-exclamation-circle fs-1 text-muted"></i>
                <p className="mt-2 text-muted">{error}</p>
              </div>
            ) : logistics ? (
              <div>
                {/* Header info */}
                <div className="d-flex flex-wrap gap-4 mb-4 p-3 bg-light rounded-3">
                  {logistics.tracking_number && (
                    <div>
                      <small className="text-muted d-block">运单编号</small>
                      <span className="fw-semibold">{logistics.tracking_number}</span>
                    </div>
                  )}
                  {logistics.carrier && (
                    <div>
                      <small className="text-muted d-block">快递公司</small>
                      <span className="fw-semibold">{logistics.carrier}</span>
                    </div>
                  )}
                  <div>
                    <small className="text-muted d-block">当前状态</small>
                    <span
                      className="badge rounded-pill"
                      style={{
                        backgroundColor: statusColor,
                        color: 'var(--jjk-bg)',
                      }}
                    >
                      {statusText}
                    </span>
                  </div>
                  {logistics.estimated_delivery && (
                    <div>
                      <small className="text-muted d-block">预计送达</small>
                      <span className="fw-semibold">
                        {new Date(logistics.estimated_delivery).toLocaleDateString('zh-CN')}
                      </span>
                    </div>
                  )}
                </div>

                {/* Timeline */}
                {logistics.events.length === 0 ? (
                  <div className="text-center py-3 text-muted">暂无物流动态</div>
                ) : (
                  <div className="position-relative">
                    {/* Vertical line */}
                    <div
                      className="position-absolute"
                      style={{
                        left: '11px',
                        top: '8px',
                        bottom: '8px',
                        width: '2px',
                        backgroundColor: '#dee2e6',
                      }}
                    />
                    {logistics.events.map((event, index) => (
                      <div key={index} className="d-flex gap-3 mb-3 position-relative">
                        {/* Dot */}
                        <div
                          className="flex-shrink-0 rounded-circle d-flex align-items-center justify-content-center"
                          style={{
                            width: '24px',
                            height: '24px',
                            backgroundColor: index === 0 ? '#ff4757' : '#e9ecef',
                            zIndex: 1,
                          }}
                        >
                          {index === 0 && (
                            <i className="bi bi-truck" style={{ fontSize: '12px', color: 'var(--jjk-bg)' }}></i>
                          )}
                        </div>
                        {/* Content */}
                        <div className="flex-grow-1" style={{ paddingBottom: '8px' }}>
                          <div className="fw-semibold" style={{ fontSize: '0.9rem' }}>
                            {event.description}
                          </div>
                          <div className="text-muted" style={{ fontSize: '0.8rem' }}>
                            {event.time && new Date(event.time).toLocaleString('zh-CN')}
                          </div>
                          {event.location && (
                            <div className="text-muted" style={{ fontSize: '0.8rem' }}>
                              <i className="bi bi-geo-alt me-1"></i>
                              {event.location}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : null}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogisticsModal;
