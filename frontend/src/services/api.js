import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8765';

export const api = axios.create({ baseURL: API_BASE_URL, timeout: 10000 });

export const authService = { login: (rut, password) => api.post('/auth/login', { rut, password }).then(r => r.data) };
export const inventoryService = {
  list: (search = '') => api.get('/inventory', { params: { search } }).then(r => r.data),
  byBarcode: barcode => api.get(`/inventory/barcode/${barcode}`).then(r => r.data),
  create: payload => api.post('/inventory', payload).then(r => r.data),
};
export const salesService = { create: payload => api.post('/sales', payload).then(r => r.data) };
export const scannerWsUrl = () => API_BASE_URL.replace(/^http/, 'ws') + '/ws/scanner';

export const cashService = { get: fecha => api.get(`/cash-register/${fecha}`).then(r => r.data), create: payload => api.post('/cash-register', payload).then(r => r.data) };

export const clientService = { list: (search = '') => api.get('/clients', { params: { search } }).then(r => r.data), create: payload => api.post('/clients', payload).then(r => r.data), credit: rut => api.get(`/clients/${rut}/credit`).then(r => r.data) };
