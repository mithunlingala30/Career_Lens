import { Link } from 'react-router-dom';
import { ScanSearch } from 'lucide-react';

export default function Logo({ to = '/' }) {
  return (
    <Link to={to} className="flex items-center gap-3" aria-label="CareerLens home">
      <span className="icon-chip" style={{ background: 'linear-gradient(135deg,#2f6bff,#ff3d95)', boxShadow: '4px 6px 14px rgba(122,60,255,.35)', width: '2.6rem', height: '2.6rem' }}><ScanSearch size={21} /></span>
      <span className="font-display text-xl font-extrabold">Career<span className="grad-text">Lens</span></span>
    </Link>
  );
}
