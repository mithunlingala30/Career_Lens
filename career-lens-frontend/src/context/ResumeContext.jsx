import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { Resumes } from '../services/api';
import { useAuth } from './AuthContext';

const Ctx = createContext(null);
export const useResume = () => useContext(Ctx);

/** Holds the candidate's resume list and the selected resume (kept in memory, never in browser storage). */
export function ResumeProvider({ children }) {
  const { user } = useAuth();
  const [resumes, setResumes] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [ready, setReady] = useState(false);

  const refresh = useCallback(async (selectId) => {
    const list = await Resumes.list();
    setResumes(list);
    setActiveId((cur) => selectId ?? (list.some((r) => r.id === cur) ? cur : list[0]?.id ?? null));
    setReady(true);
    return list;
  }, []);

  useEffect(() => { if (user?.role === 'candidate') refresh().catch(() => setReady(true)); }, [user, refresh]);

  const active = resumes.find((r) => r.id === activeId) || null;
  return <Ctx.Provider value={{ resumes, active, activeId, setActiveId, refresh, ready }}>{children}</Ctx.Provider>;
}
