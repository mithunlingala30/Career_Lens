import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { LayoutDashboard, UploadCloud, Gauge, Briefcase, Compass, Radar, History, UserCircle, LogOut, Menu, X, ShieldCheck, FileText } from 'lucide-react';
import Logo from '../components/Logo';
import { useAuth } from '../context/AuthContext';
import { ResumeProvider, useResume } from '../context/ResumeContext';

const CANDIDATE = [
  ['/app/dashboard', 'Dashboard', LayoutDashboard], ['/app/upload', 'Resume Upload', UploadCloud], ['/app/evaluation', 'Evaluation', Gauge],
  ['/app/jobs', 'Job Matching', Briefcase], ['/app/careers', 'Careers', Compass], ['/app/skill-gaps', 'Skill Gaps', Radar],
  ['/app/history', 'History', History], ['/app/profile', 'My Profile', UserCircle],
];
const ADMIN = [['/admin', 'Admin Dashboard', ShieldCheck]];

function ResumePicker() {
  const { resumes, activeId, setActiveId } = useResume();
  if (!resumes.length) return null;
  return (
    <label className="flex items-center gap-2">
      <FileText size={16} className="text-bright-violet" />
      <span className="sr-only">Active resume</span>
      <select className="field !w-auto max-w-[210px] !py-2 text-sm" value={activeId ?? ''} onChange={(e) => setActiveId(Number(e.target.value))}>
        {resumes.map((r) => <option key={r.id} value={r.id}>{r.original_filename}</option>)}
      </select>
    </label>
  );
}

function Shell() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const [open, setOpen] = useState(false);
  const items = user.role === 'admin' ? ADMIN : CANDIDATE;
  const side = (
    <nav className="flex h-full flex-col gap-2" aria-label="Main">
      <div className="mb-6 px-2"><Logo to={user.role === 'admin' ? '/admin' : '/app/dashboard'} /></div>
      {items.map(([to, label, Icon]) => (
        <NavLink key={to} to={to} end onClick={() => setOpen(false)} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}><Icon size={19} />{label}</NavLink>
      ))}
      <button className="nav-link mt-auto" onClick={() => { logout(); nav('/'); }}><LogOut size={19} />Sign out</button>
    </nav>
  );
  return (
    <div className="min-h-screen lg:flex">
      <aside className="neu fixed inset-y-4 left-4 z-30 hidden w-64 p-4 lg:block">{side}</aside>
      {open && <div className="fixed inset-0 z-40 bg-navy/40 backdrop-blur-sm lg:hidden" onClick={() => setOpen(false)}><aside className="neu m-3 h-[calc(100%-1.5rem)] w-72 p-4" onClick={(e) => e.stopPropagation()}>{side}</aside></div>}
      <div className="flex-1 lg:ml-72">
        <header className="sticky top-0 z-20 flex items-center justify-between gap-3 px-4 py-4 sm:px-8" style={{ background: 'linear-gradient(var(--bg) 70%, transparent)' }}>
          <button className="btn btn-sm lg:hidden" aria-label="Open menu" onClick={() => setOpen(true)}>{open ? <X size={18} /> : <Menu size={18} />}</button>
          <div className="hidden text-sm text-muted lg:block">Welcome back, <b className="text-navy">{user.full_name.split(' ')[0]}</b></div>
          <div className="flex items-center gap-3">
            {user.role === 'candidate' && <ResumePicker />}
            <div className="icon-chip !h-10 !w-10 !rounded-full text-sm font-extrabold" style={{ background: 'linear-gradient(135deg,#7a3cff,#ff3d95)' }} title={user.email}>{user.full_name[0]?.toUpperCase()}</div>
          </div>
        </header>
        <main className="px-4 pb-12 pt-2 sm:px-8"><Outlet /></main>
      </div>
    </div>
  );
}

export default function AppLayout() {
  return <ResumeProvider><Shell /></ResumeProvider>;
}
