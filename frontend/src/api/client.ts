import axios from 'axios';

# 前端 API 基础地址 — 部署时改为 Render 后端地址
# GitHub Pages: http://localhost:5173/api/v1 (本地开发)
# Render: https://ecommerce-final.onrender.com/api/v1 (线上)
const API_BASE = import.meta.env.DEV ? '/api/v1' : 'https://ecommerce-final.onrender.com/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：自动添加 token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：处理 401 未授权，但排除登录接口自身
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 判断是否是登录请求本身的 401（用户名或密码错误）
      const isLoginRequest = error.config?.url?.includes('/auth/login');
      
      if (!isLoginRequest) {
        // 只有非登录请求的 401 才清除 token 并跳转登录页
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;