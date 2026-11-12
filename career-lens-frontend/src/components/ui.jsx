import { useId, useEffect } from 'react';
import { Loader2, AlertTriangle, X, Inbox } from 'lucide-react';
import { Link } from 'react-router-dom';

export const PALETTE = ['#2f6bff', '#7a3cff', '#ff3d95', '#ff8a1f', '#00c4a7', '#ffc226', '#22c55e'];
export const GRADS = {
  blue: 'linear-gradient(135deg,#2f6bff,#7a3cff)', pink: 'linear-gradient(135deg,#ff3d95,#ff8a1f)',
  teal: 'linear-gradient(135deg,#00c4a7,#2f6bff)', orange: 'linear-gradient(135deg,#ffc226,#ff8a1f)',
  violet: 'linear-gradient(135deg,#7a3cff,#ff3d95)', green: 'linear-gradient(135deg,#22c55e,#00c4a7)',
};
export const scoreColor = (v) => (v >= 75 ? '#00c4a7' : v >= 50 ? '#2f6bff' : v >= 30 ? '#ff8a1f' : '#ff3d95');

export const Card = ({ className = '', children, ...p }) => <div className={`neu p-5 sm:p-6 ${className}`} {...p}>{children}</div>;

export function Btn({ variant = '', loading, icon: Icon, children, className = '', size = '', as: As = 'button', ...p }) {
  return (
    <As className={`btn ${variant ? 'btn-' + variant : ''} ${size === 'sm' ? 'btn-sm' : ''} ${className}`} disabled={loading || p.disabled} {...p}>
      {loading ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : Icon && <Icon size={size === 'sm' ? 14 : 17} />}
      {children}
    </As>
  );
}

export const Spinner = ({ label = 'Loading…' }) => (
  <div role="status" className="flex flex-col items-center justify-center gap-3 py-16 text-muted">
    <div className="neu-sm grid h-14 w-14 place-items-center rounded-full"><Loader2 size={26} className="text-bright-violet" style={{ animation: 'spin 1s linear infinite' }} /></div>
    <span className="text-sm font-semibold">{label}</span>
  </div>
);

export function ErrorBox({ error, onRetry }) {
  if (!error) return null;
  return (
    <div role="alert" className="neu-inset flex items-start gap-3 p-4 text-sm">
      <AlertTriangle className="mt-0.5 shrink-0 text-bright-pink" size={18} />
      <div className="flex-1 font-semibold text-navy">{error}</div>
      {onRetry && <button className="btn btn-sm" onClick={onRetry}>Retry</button>}
    </div>
  );
}

export const Notice = ({ tone = 'blue', children }) => (
  <div role="status" className="neu-inset p-4 text-sm font-semibold" style={{ color: tone === 'green' ? '#009e87' : tone === 'pink' ? '#d91e78' : '#2f6bff' }}>{children}</div>
);

export function Empty({ title, text, action, to }) {
  return (
    <Card className="flex flex-col items-center gap-3 py-12 text-center">
      <div className="icon-chip" style={{ background: GRADS.violet }}><Inbox size={22} /></div>
      <h3 className="text-lg font-bold">{title}</h3>
      <p className="max-w-md text-sm text-muted">{text}</p>
      {to && <Link to={to} className="btn btn-primary">{action}</Link>}
    </Card>
  );
}

export const PageHeader = ({ title, subtitle, children }) => (
  <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
    <div>
      <h1 className="text-2xl font-extrabold sm:text-3xl">{title}</h1>
      {subtitle && <p className="mt-1 text-sm text-muted">{subtitle}</p>}
    </div>
    <div className="flex flex-wrap items-center gap-3">{children}</div>
  </div>
);

export function ProgressBar({ value = 0, color, grad }) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div className="track" role="progressbar" aria-valuenow={Math.round(v)} aria-valuemin={0} aria-valuemax={100}>
      <div style={{ width: `${v}%`, background: grad || color || `linear-gradient(90deg,#2f6bff,#7a3cff)` }} />
    </div>
  );
}

export function ScoreRing({ value = 0, size = 150, label, sub, color }) {
  const id = useId().replace(/:/g, '');
  const r = 46, c = 2 * Math.PI * r, v = Math.max(0, Math.min(100, value));
  const col = color || scoreColor(v);
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="neu-inset grid place-items-center rounded-full" style={{ width: size, height: size }}>
        <svg viewBox="0 0 120 120" width={size * 0.86} height={size * 0.86} style={{ transform: 'rotate(-90deg)' }}>
          <defs><linearGradient id={id} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor={col} /><stop offset="1" stopColor="#7a3cff" /></linearGradient></defs>
          <circle cx="60" cy="60" r={r} fill="none" stroke="#d3daec" strokeWidth="11" />
          <circle cx="60" cy="60" r={r} fill="none" stroke={`url(#${id})`} strokeWidth="11" strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c * (1 - v / 100)} style={{ transition: 'stroke-dashoffset 1s ease' }} />
          <text x="60" y="66" textAnchor="middle" fontSize="25" fontWeight="800" fill="#14204a" style={{ transform: 'rotate(90deg)', transformOrigin: '60px 60px', fontFamily: 'Sora' }}>{Math.round(v)}{sub === '%' ? '%' : ''}</text>
        </svg>
      </div>
      {label && <span className="text-sm font-bold text-muted">{label}</span>}
    </div>
  );
}

export function StatCard({ icon: Icon, label, value, grad = 'blue', hint }) {
  return (
    <Card className="flex items-center gap-4">
      <div className="icon-chip shrink-0" style={{ background: GRADS[grad], boxShadow: '4px 6px 14px rgba(47,107,255,.3)' }}><Icon size={22} /></div>
      <div className="min-w-0">
        <div className="text-xs font-bold text-muted">{label}</div>
        <div className="font-display text-2xl font-extrabold">{value}</div>
        {hint && <div className="truncate text-xs text-muted">{hint}</div>}
      </div>
    </Card>
  );
}

const CHIP = { blue: '#2f6bff', green: '#009e87', pink: '#e0207f', orange: '#e87400', violet: '#7a3cff', gray: '#5b6892' };
export const Chip = ({ color = 'blue', children, title }) => <span title={title} className="chip" style={{ color: CHIP[color] }}>{children}</span>;

export function Modal({ open, onClose, title, children, wide }) {
  useEffect(() => {
    if (!open) return;
    const h = (e) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', h);
    return () => document.removeEventListener('keydown', h);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 grid place-items-center overflow-y-auto bg-navy/40 p-4 backdrop-blur-sm" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div role="dialog" aria-modal="true" aria-label={title} className={`neu my-6 w-full p-6 ${wide ? 'max-w-3xl' : 'max-w-lg'}`}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-extrabold">{title}</h2>
          <button className="btn btn-sm" aria-label="Close" onClick={onClose}><X size={16} /></button>
        </div>
        {children}
      </div>
    </div>
  );
}

export const Field = ({ label, children, className = '' }) => <div className={className}><label className="label">{label}</label>{children}</div>;
export const fmtDate = (d) => (d ? new Date(d).toLocaleString(undefined, { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '');
export const EDU_LEVELS = [[0, 'Not specified'], [1, 'Diploma'], [2, "Bachelor's"], [3, "Master's"], [4, 'Doctorate']];
export const tipStyle = { borderRadius: 14, border: 0, background: '#e6ebf7', boxShadow: '6px 6px 14px #c3cbe0, -6px -6px 14px #fff', fontSize: 12 };
