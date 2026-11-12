import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { Auth } from '../services/api';

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!localStorage.getItem('cl_token'));

  useEffect(() => {
    if (!localStorage.getItem('cl_token')) return;
    Auth.me().then(setUser).catch(() => localStorage.removeItem('cl_token')).finally(() => setLoading(false));
  }, []);

  const finish = useCallback((res) => { localStorage.setItem('cl_token', res.access_token); setUser(res.user); return res.user; }, []);
  const login = useCallback((email, password, role) => Auth.login({ email, password, role }).then(finish), [finish]);
  const register = useCallback((full_name, email, password) => Auth.register({ full_name, email, password }).then(finish), [finish]);
  const logout = useCallback(() => { localStorage.removeItem('cl_token'); setUser(null); }, []);

  return <Ctx.Provider value={{ user, loading, login, register, logout }}>{children}</Ctx.Provider>;
}
