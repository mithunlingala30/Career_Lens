import { useState } from 'react';
import { Link } from 'react-router-dom';
import { UploadCloud, Compass, FileSearch, Target, Route, ShieldCheck, BarChart3, Sigma, Brain, Github, Menu, X, ArrowRight, CheckCircle2 } from 'lucide-react';
import Logo from '../components/Logo';
import { GRADS, ScoreRing } from '../components/ui';
import { useAuth } from '../context/AuthContext';

const NAV = [['Home', '#home'], ['Features', '#features'], ['How It Works', '#how'], ['About', '#about']];
const FEATURES = [
  [FileSearch, 'Smart resume parsing', 'PDF and DOCX resumes become structured profiles: education, skills, experience, certifications and projects.', 'blue'],
  [Target, 'Job compatibility', 'Skill vectors, Bayes posteriors and latent SVD factors rank every job by true fit.', 'pink'],
  [Route, 'Career pathways', 'See readiness, missing skills and a Markov-chain forecast of how fast you can level up.', 'teal'],
  [BarChart3, 'Honest statistics', 'Gaussian percentiles and a hypothesis test prove the matcher beats plain keyword search.', 'orange'],
  [ShieldCheck, 'Private by design', 'JWT-secured accounts; your resumes live in your own Firebase-backed workspace.', 'violet'],
  [Sigma, 'Downloadable reports', 'Export a polished PDF with scores, gaps and a personalised development plan.', 'green'],
];
const MODULES = [
  ['Module 1', 'Resume Data Analysis', 'Document processing and text analysis extract every detail, which you can correct before scoring.', 'blue'],
  ['Module 2', 'Evaluation and Job Matching', 'Bayes theorem, conditional probability, inner products and SVD turn skills into a 0-100 score.', 'pink'],
  ['Module 3', 'Career Recommendation', 'Gaussian analysis, Markov chains and hypothesis testing guide your next career move.', 'teal'],
];
const STEPS = ['Create your free account', 'Upload your resume (PDF or DOCX)', 'Review and correct extracted details', 'Get scores, matches and a skill-gap plan'];

export default function Landing() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const home = user ? (user.role === 'admin' ? '/admin' : '/app/dashboard') : '/login';
  return (
    <div>
      <header className="sticky top-0 z-30 px-3 pt-3 sm:px-6">
        <div className="neu glass mx-auto flex max-w-6xl items-center justify-between !rounded-3xl px-5 py-3">
          <Logo />
          <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">{NAV.map(([n, h]) => <a key={n} href={h} className="rounded-xl px-4 py-2 text-sm font-bold text-muted transition hover:text-bright-violet">{n}</a>)}</nav>
          <div className="hidden items-center gap-3 md:flex">
            {user ? <Link to={home} className="btn btn-primary btn-sm">Open dashboard</Link> : <><Link to="/login" className="btn btn-sm">Login</Link><Link to="/register" className="btn btn-primary btn-sm">Register</Link></>}
          </div>
          <button className="btn btn-sm md:hidden" aria-label="Menu" onClick={() => setOpen(!open)}>{open ? <X size={18} /> : <Menu size={18} />}</button>
        </div>
        {open && <div className="neu mx-auto mt-3 flex max-w-6xl flex-col gap-2 p-4 md:hidden">{NAV.map(([n, h]) => <a key={n} href={h} onClick={() => setOpen(false)} className="nav-link">{n}</a>)}
          <div className="flex gap-3 pt-2"><Link to="/login" className="btn flex-1">Login</Link><Link to="/register" className="btn btn-primary flex-1">Register</Link></div></div>}
      </header>

      <section id="home" className="mx-auto grid max-w-6xl items-center gap-12 px-5 pb-20 pt-16 lg:grid-cols-2">
        <div>
          <span className="chip mb-5 text-bright-violet"><Brain size={14} /> Automated resume evaluation platform</span>
          <h1 className="text-4xl font-extrabold leading-[1.1] sm:text-5xl lg:text-[3.4rem]">Build Your Career with <span className="grad-text">Intelligent Resume Insights</span></h1>
          <p className="mt-5 max-w-xl text-lg text-muted">CareerLens reads your resume, scores it from 0 to 100, matches it against real job requirements, exposes skill gaps and recommends the career paths where you are most ready to grow.</p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link to={user ? '/app/upload' : '/register'} className="btn btn-primary"><UploadCloud size={18} />Upload Resume</Link>
            <a href="#modules" className="btn btn-orange"><Compass size={18} />Explore Careers</a>
          </div>
          <ul className="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-sm font-semibold text-muted">{['PDF & DOCX', 'Firebase cloud storage', 'PDF reports'].map((t) => <li key={t} className="flex items-center gap-2"><CheckCircle2 size={16} className="text-bright-teal" />{t}</li>)}</ul>
        </div>
        <div className="relative" aria-hidden="true">
          <div className="neu animate-floaty p-6">
            <div className="mb-5 flex items-center justify-between"><b className="font-display">Resume evaluation</b><span className="chip text-bright-teal">Live preview</span></div>
            <div className="flex items-center justify-around"><ScoreRing value={86} size={130} label="Resume score" /><ScoreRing value={78} size={130} label="Job match" sub="%" color="#ff3d95" /></div>
            <div className="mt-6 space-y-3">
              {[['Python', 92, GRADS.blue], ['SQL', 80, GRADS.teal], ['Docker', 45, GRADS.pink]].map(([n, v, g]) => <div key={n}><div className="mb-1 flex justify-between text-xs font-bold text-muted"><span>{n}</span><span>{v}%</span></div><div className="track"><div style={{ width: `${v}%`, background: g }} /></div></div>)}
            </div>
          </div>
          <div className="neu-sm absolute -bottom-6 -left-4 hidden items-center gap-3 px-4 py-3 sm:flex"><span className="icon-chip !h-10 !w-10" style={{ background: GRADS.orange }}><Target size={18} /></span><div className="text-xs"><b>Top match</b><div className="text-muted">Data Scientist</div></div></div>
        </div>
      </section>

      <section id="features" className="mx-auto max-w-6xl px-5 py-16">
        <h2 className="text-center text-3xl font-extrabold">Everything you need to know where you <span className="grad-text">stand</span></h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-muted">Six capabilities, one workspace, all driven by real mathematics rather than guesswork.</p>
        <div className="mt-12 grid gap-7 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(([Icon, t, d, g]) => <div key={t} className="neu p-6 transition hover:-translate-y-1"><div className="icon-chip mb-4" style={{ background: GRADS[g], boxShadow: '4px 6px 14px rgba(47,107,255,.28)' }}><Icon size={22} /></div><h3 className="text-lg font-bold">{t}</h3><p className="mt-2 text-sm text-muted">{d}</p></div>)}
        </div>
      </section>

      <section id="modules" className="mx-auto max-w-6xl px-5 py-16">
        <h2 className="text-center text-3xl font-extrabold">Three modules, one <span className="grad-text">career engine</span></h2>
        <div className="mt-12 grid gap-7 lg:grid-cols-3">
          {MODULES.map(([k, t, d, g]) => <div key={k} className="neu relative overflow-hidden p-7"><div className="absolute -right-6 -top-6 h-24 w-24 rounded-full opacity-90" style={{ background: GRADS[g] }} /><span className="chip relative text-bright-violet">{k}</span><h3 className="mt-4 text-xl font-extrabold">{t}</h3><p className="mt-2 text-sm text-muted">{d}</p></div>)}
        </div>
      </section>

      <section id="how" className="mx-auto max-w-6xl px-5 py-16">
        <h2 className="text-center text-3xl font-extrabold">How it works</h2>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((s, i) => <div key={s} className="neu p-6 text-center"><div className="icon-chip mx-auto mb-4 !h-14 !w-14 font-display text-xl font-extrabold" style={{ background: GRADS[['blue', 'pink', 'teal', 'orange'][i]] }}>{i + 1}</div><p className="font-bold">{s}</p></div>)}
        </div>
      </section>

      <section id="about" className="mx-auto max-w-4xl px-5 py-16">
        <div className="neu p-8 text-center sm:p-12">
          <h2 className="text-3xl font-extrabold">About CareerLens</h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted">CareerLens helps students and job seekers understand their career readiness. It applies probability, linear algebra and statistics to resumes and job requirements so that every number on screen can be traced back to a transparent calculation.</p>
          <Link to={user ? home : '/register'} className="btn btn-primary mt-8">Get started free <ArrowRight size={18} /></Link>
        </div>
      </section>

      <footer className="mx-auto max-w-6xl px-5 pb-10 pt-6">
        <div className="neu-inset flex flex-wrap items-center justify-between gap-4 px-6 py-5 text-sm text-muted">
          <Logo /><span>© {new Date().getFullYear()} CareerLens. Automated resume evaluation and career recommendation.</span>
          <span className="flex items-center gap-2"><Github size={16} />React · FastAPI · Firebase Firestore</span>
        </div>
      </footer>
    </div>
  );
}
