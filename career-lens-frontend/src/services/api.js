import axios from 'axios';

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api' });

api.interceptors.request.use((cfg) => {
  const t = localStorage.getItem('cl_token');
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});
api.interceptors.response.use(
  (r) => r,
  (err) => {
    const url = err.config?.url || '';
    if (err.response?.status === 401 && !url.includes('/auth/login') && !url.includes('/auth/register')) {
      localStorage.removeItem('cl_token');
      if (!window.location.pathname.startsWith('/login')) window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export function errMsg(e) {
  if (!e) return '';
  if (e.code === 'ERR_NETWORK') return 'Cannot reach the server. Check that the backend is running on port 8000.';
  const d = e.response?.data?.detail;
  if (Array.isArray(d)) return d.map((x) => (x.msg || '').replace('Value error, ', '')).join('. ');
  return d || e.message || 'Something went wrong';
}

const g = (u, p) => api.get(u, { params: p }).then((r) => r.data);
const post = (u, b, c) => api.post(u, b, c).then((r) => r.data);

export const Auth = {
  register: (b) => post('/auth/register', b),
  login: (b) => post('/auth/login', b),
  me: () => g('/auth/me'),
  forgot: (email) => post('/auth/forgot-password', { email }),
  reset: (token, new_password) => post('/auth/reset-password', { token, new_password }),
};
export const Resumes = {
  list: () => g('/resumes'),
  get: (id) => g(`/resumes/${id}`),
  upload: (file, onProgress) => {
    const fd = new FormData();
    fd.append('file', file);
    return post('/resumes/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' }, onUploadProgress: (e) => onProgress?.(Math.round((e.loaded * 100) / (e.total || 1))) });
  },
  remove: (id) => api.delete(`/resumes/${id}`).then((r) => r.data),
  fileBlob: (id) => api.get(`/resumes/${id}/file`, { responseType: 'blob' }).then((r) => r.data),
};
export const Analysis = {
  extract: (id) => post(`/analysis/extract/${id}`),
  get: (id) => g(`/analysis/${id}`),
  update: (id, body) => api.put(`/analysis/${id}`, body).then((r) => r.data),
};
export const Jobs = {
  list: (p) => g('/jobs', p),
  categories: () => g('/jobs/categories'),
  create: (b) => post('/jobs', b),
  update: (id, b) => api.put(`/jobs/${id}`, b).then((r) => r.data),
  remove: (id) => api.delete(`/jobs/${id}`).then((r) => r.data),
  extractSkills: (description) => post('/jobs/extract-skills', { description }),
  renameCategory: (old, neu) => api.put('/jobs/categories/rename', { old, new: neu }).then((r) => r.data),
};
export const Evaluation = {
  run: (rid, jid) => post(`/evaluation/${rid}/${jid}`),
  list: (rid) => g(`/evaluation/${rid}`),
  get: (rid, jid) => g(`/evaluation/${rid}`, { job_id: jid }),
  history: () => g('/evaluation/history'),
  validation: () => g('/evaluation/validation'),
};
export const Matching = { run: (rid) => post(`/matching/${rid}`), get: (rid) => g(`/matching/${rid}`) };
export const Recs = { run: (rid) => post(`/recommendations/${rid}`), get: (rid) => g(`/recommendations/${rid}`) };
export const Gaps = { get: (rid, jid) => g(`/skill-gaps/${rid}`, jid ? { job_id: jid } : undefined) };
export const Dashboard = { candidate: () => g('/dashboard/candidate'), admin: () => g('/dashboard/admin') };
export const Reports = {
  pdf: async (evalId) => {
    const r = await api.get(`/reports/${evalId}/pdf`, { responseType: 'blob' });
    const url = URL.createObjectURL(r.data);
    const a = document.createElement('a');
    a.href = url; a.download = `careerlens-report-${evalId}.pdf`; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  },
};
export default api;
