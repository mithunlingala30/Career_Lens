import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, LogIn, UserPlus, Check, X, ShieldCheck, User } from 'lucide-react';
import Logo from '../components/Logo';
import { Btn, ErrorBox, Field, GRADS } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { errMsg } from '../services/api';

export const pwRules = (p) => [['8+ characters', p.length >= 8], ['Uppercase letter', /[A-Z]/.test(p)], ['Lowercase letter', /[a-z]/.test(p)], ['A number', /\d/.test(p)]];

export default function Login({ mode }) {
  const { login, register } = useAuth();
  const nav = useNavigate();
  const from = useLocation().state?.from;
  const isReg = mode === 'register';
  const [role, setRole] = useState('candidate');
  const [f, setF] = useState({ name: '', email: '', password: '', confirm: '' });
  const [show, setShow] = useState(false);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const rules = pwRules(f.password);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setErr('');
    if (isReg) {
      if (rules.some(([, ok]) => !ok)) return setErr('Please satisfy every password requirement.');
      if (f.password !== f.confirm) return setErr('Passwords do not match.');
    }
    setBusy(true);
    try {
      const u = isReg ? await register(f.name, f.email, f.password) : await login(f.email, f.password, role);
      nav(u.role === 'admin' ? '/admin' : from?.startsWith('/app') ? from : '/app/dashboard', { replace: true });
    } catch (ex) { setErr(errMsg(ex)); } finally { setBusy(false); }
  }

  return (
    <div className="grid min-h-screen place-items-center px-4 py-10">
      <div className="grid w-full max-w-5xl overflow-hidden lg:grid-cols-2 neu !p-0">
        <div className="relative hidden flex-col justify-between p-10 text-white lg:flex" style={{ background: 'linear-gradient(145deg,#2f6bff,#7a3cff 55%,#ff3d95)' }}>
          <div><div className="mb-10 flex items-center gap-2 font-display text-2xl font-extrabold">CareerLens</div>
            <h2 className="text-3xl font-extrabold leading-tight">Know your career readiness in minutes.</h2>
            <p className="mt-4 text-white/85">Upload a resume, see exactly which skills you have, which you lack, and which careers fit you best.</p></div>
          <ul className="space-y-3 text-sm font-semibold">{['Resume score out of 100', 'Ranked job compatibility', 'Skill-gap learning plan', 'Downloadable PDF report'].map((t) => <li key={t} className="flex items-center gap-2"><Check size={16} />{t}</li>)}</ul>
        </div>
        <div className="p-7 sm:p-10">
          <div className="mb-6 lg:hidden"><Logo /></div>
          <h1 className="text-2xl font-extrabold">{isReg ? 'Create your account' : 'Welcome back'}</h1>
          <p className="mb-6 mt-1 text-sm text-muted">{isReg ? 'Register as a candidate to start evaluating your resume.' : 'Sign in to continue to your workspace.'}</p>
          {!isReg && (
            <div className="neu-inset mb-5 grid grid-cols-2 gap-1 p-1" role="tablist" aria-label="Login type">
              {[['candidate', 'Candidate', User], ['admin', 'Admin', ShieldCheck]].map(([k, l, Icon]) => (
                <button key={k} type="button" role="tab" aria-selected={role === k} onClick={() => setRole(k)} className="flex items-center justify-center gap-2 rounded-xl py-2.5 text-sm font-bold transition"
                  style={role === k ? { background: GRADS.blue, color: '#fff', boxShadow: '3px 5px 12px rgba(47,107,255,.35)' } : { color: '#5b6892' }}><Icon size={16} />{l}</button>
              ))}
            </div>)}
          <form onSubmit={submit} className="space-y-4" noValidate>
            {isReg && <Field label="Full name"><input className="field" value={f.name} onChange={set('name')} required minLength={2} autoComplete="name" placeholder="Priya Ramesh" /></Field>}
            <Field label="Email"><input className="field" type="email" value={f.email} onChange={set('email')} required autoComplete="email" placeholder={role === 'admin' && !isReg ? 'admin@careerlens.com' : 'you@example.com'} /></Field>
            <Field label="Password">
              <div className="relative">
                <input className="field !pr-12" type={show ? 'text' : 'password'} value={f.password} onChange={set('password')} required autoComplete={isReg ? 'new-password' : 'current-password'} placeholder="••••••••" />
                <button type="button" aria-label={show ? 'Hide password' : 'Show password'} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted" onClick={() => setShow(!show)}>{show ? <EyeOff size={18} /> : <Eye size={18} />}</button>
              </div>
            </Field>
            {isReg && <>
              <Field label="Confirm password"><input className="field" type={show ? 'text' : 'password'} value={f.confirm} onChange={set('confirm')} required autoComplete="new-password" /></Field>
              <ul className="grid grid-cols-2 gap-2 text-xs font-semibold">{rules.map(([t, ok]) => <li key={t} className="flex items-center gap-1.5" style={{ color: ok ? '#009e87' : '#8d98bb' }}>{ok ? <Check size={14} /> : <X size={14} />}{t}</li>)}</ul>
            </>}
            <ErrorBox error={err} />
            <Btn variant="primary" className="w-full" loading={busy} icon={isReg ? UserPlus : LogIn} type="submit">{isReg ? 'Create account' : 'Sign in'}</Btn>
          </form>
          <div className="mt-6 flex flex-wrap justify-between gap-2 text-sm font-semibold">
            {!isReg && <Link to="/forgot-password" className="text-bright-blue">Forgot password?</Link>}
            {isReg ? <span className="text-muted">Have an account? <Link to="/login" className="text-bright-blue">Sign in</Link></span>
              : <span className="text-muted">New here? <Link to="/register" className="text-bright-blue">Register</Link></span>}
          </div>
          <Link to="/" className="mt-4 inline-block text-xs font-semibold text-muted">← Back to home</Link>
        </div>
      </div>
    </div>
  );
}
