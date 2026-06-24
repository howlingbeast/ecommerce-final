// src/types/logistics.ts
export interface LogisticsEvent {
  time: string;
  description: string;
  location: string | null;
}

export interface Logistics {
  id: number;
  order_id: number;
  tracking_number: string | null;
  carrier: string | null;
  status: 'pending' | 'shipped' | 'in_transit' | 'delivering' | 'delivered' | 'exception';
  events: LogisticsEvent[];
  estimated_delivery: string | null;
  created_at: string;
  updated_at: string;
}

// 物流状态中文映射
export const LogisticsStatusText: Record<string, string> = {
  pending: '待发货',
  shipped: '已发货',
  in_transit: '运输中',
  delivering: '派送中',
  delivered: '已签收',
  exception: '异常',
};

// 物流状态对应的颜色
export const LogisticsStatusColor: Record<string, string> = {
  pending: '#6c757d',
  shipped: '#0d6efd',
  in_transit: '#ffc107',
  delivering: '#fd7e14',
  delivered: '#198754',
  exception: '#dc3545',
};
