import { useState } from 'react';
import { Link } from 'react-router-dom';
import { KeyRound, Mail } from 'lucide-react';
import Logo from '../components/Logo';
import { Btn, ErrorBox, Field, Notice } from '../components/ui';
import { Auth, errMsg } from '../services/api';
import { pwRules } from './Login';

export default function ForgotPassword() {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [pw, setPw] = useState('');
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);

  async function run(fn) { setErr(''); setBusy(true); try { await fn(); } catch (e) { setErr(errMsg(e)); } finally { setBusy(false); } }
  const send = (e) => { e.preventDefault(); run(async () => { const r = await Auth.forgot(email); setMsg(r.message); if (r.dev_reset_token) setToken(r.dev_reset_token); setStep(2); }); };
  const reset = (e) => { e.preventDefault(); if (pwRules(pw).some(([, ok]) => !ok)) return setErr('Password needs 8+ characters with upper, lower case and a number.');
    run(async () => { const r = await Auth.reset(token, pw); setMsg(r.message); setStep(3); }); };

  return (
    <div className="grid min-h-screen place-items-center px-4">
      <div className="neu w-full max-w-md p-8">
        <Logo />
        <h1 className="mb-1 mt-6 text-2xl font-extrabold">Reset your password</h1>
        {step === 1 && <form onSubmit={send} className="mt-5 space-y-4"><p className="text-sm text-muted">Enter your account email and we will generate a reset token.</p>
          <Field label="Email"><input className="field" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" /></Field>
          <ErrorBox error={err} /><Btn variant="primary" className="w-full" icon={Mail} loading={busy} type="submit">Generate reset token</Btn></form>}
        {step === 2 && <form onSubmit={reset} className="mt-5 space-y-4"><Notice>{msg} {token ? 'Development mode: the token has been filled in for you (no email server is bundled).' : 'Paste the token you received.'}</Notice>
          <Field label="Reset token"><input className="field" required value={token} onChange={(e) => setToken(e.target.value)} /></Field>
          <Field label="New password"><input className="field" type="password" required value={pw} onChange={(e) => setPw(e.target.value)} autoComplete="new-password" /></Field>
          <ErrorBox error={err} /><Btn variant="teal" className="w-full" icon={KeyRound} loading={busy} type="submit">Update password</Btn></form>}
        {step === 3 && <div className="mt-5 space-y-4"><Notice tone="green">{msg}</Notice><Link to="/login" className="btn btn-primary w-full">Back to sign in</Link></div>}
        {step !== 3 && <Link to="/login" className="mt-5 inline-block text-sm font-semibold text-bright-blue">← Back to sign in</Link>}
      </div>
    </div>
  );
}
