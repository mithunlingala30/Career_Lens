import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, MapPin, Building2, Clock, ChevronDown, ChevronUp, GraduationCap, Play } from 'lucide-react';
import { Matching, errMsg } from '../services/api';
import { Btn, Card, Chip, EDU_LEVELS, ErrorBox, PageHeader, ProgressBar, ScoreRing, Spinner, scoreColor } from '../components/ui';
import ResumeGate from '../components/ResumeGate';
import useFetch from '../hooks/useFetch';

function JobCard({ m }) {
  const [open, setOpen] = useState(false);
  const j = m.job;
  return (
    <Card>
      <div className="flex flex-wrap items-start gap-5">
        <ScoreRing value={m.compatibility} size={96} sub="%" />
        <div className="min-w-[220px] flex-1">
          <div className="flex flex-wrap items-center gap-2"><h3 className="text-lg font-extrabold">{j.title}</h3><Chip color="violet">#{m.rank}</Chip><Chip color="blue">{j.category}</Chip></div>
          <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted"><span className="flex items-center gap-1"><Building2 size={13} />{j.company}</span>{j.location && <span className="flex items-center gap-1"><MapPin size={13} />{j.location}</span>}
            <span className="flex items-center gap-1"><Clock size={13} />{j.min_experience_years}+ yrs</span><span className="flex items-center gap-1"><GraduationCap size={13} />{EDU_LEVELS[j.min_education_level][1]}</span>{j.salary_range && <b className="text-bright-teal">{j.salary_range}</b>}</div>
          <div className="mt-3 flex flex-wrap gap-1.5">{m.matched_skills.slice(0, 6).map((s) => <Chip key={s.skill} color="green">{s.skill}</Chip>)}{m.missing_skills.slice(0, 5).map((s) => <Chip key={s.skill} color="pink">{s.skill}</Chip>)}</div>
        </div>
        <div className="flex flex-col gap-2"><Link to={`/app/evaluation?job=${j.id}`} className="btn btn-primary btn-sm">Detailed matching</Link><button className="btn btn-sm" onClick={() => setOpen(!open)}>{open ? <ChevronUp size={14} /> : <ChevronDown size={14} />} Details</button></div>
      </div>
      {open && <div className="mt-5 grid gap-5 border-t border-white/60 pt-5 md:grid-cols-2">
        <div><h4 className="mb-2 text-sm font-extrabold">Description</h4><p className="text-sm text-muted">{j.description}</p>
          <h4 className="mb-2 mt-4 text-sm font-extrabold">Required qualifications</h4><p className="text-sm text-muted">{EDU_LEVELS[j.min_education_level][1]} degree or equivalent · {j.min_experience_years} years of experience</p></div>
        <div><h4 className="mb-2 text-sm font-extrabold">Required skills</h4>
          <div className="space-y-2">{j.requirements.map((r) => { const has = m.matched_skills.some((s) => s.skill === r.skill_name); return <div key={r.skill_name}><div className="mb-1 flex justify-between text-xs font-bold"><span style={{ color: has ? '#009e87' : '#e0207f' }}>{has ? '✓' : '✗'} {r.skill_name}{r.is_mandatory && ' ★'}</span><span className="text-muted">importance {r.importance}/5</span></div><ProgressBar value={r.importance * 20} grad={has ? 'linear-gradient(90deg,#00c4a7,#22c55e)' : 'linear-gradient(90deg,#ff3d95,#ff8a1f)'} /></div>; })}</div></div>
      </div>}
    </Card>
  );
}

function Body({ resume }) {
  const { data, loading, error, reload } = useFetch(() => Matching.get(resume.id), [resume.id]);
  const [q, setQ] = useState(''); const [cat, setCat] = useState(''); const [maxExp, setMaxExp] = useState(''); const [skill, setSkill] = useState(''); const [min, setMin] = useState(0);
  const [busy, setBusy] = useState(false); const [err, setErr] = useState('');
  const matches = data?.matches || [];
  const cats = useMemo(() => [...new Set(matches.map((m) => m.job.category))].sort(), [matches]);
  const list = matches.filter((m) => {
    const j = m.job, t = `${j.title} ${j.company} ${j.description}`.toLowerCase();
    return (!q || t.includes(q.toLowerCase())) && (!cat || j.category === cat) && (maxExp === '' || j.min_experience_years <= Number(maxExp))
      && (!skill || j.requirements.some((r) => r.skill_name.toLowerCase().includes(skill.toLowerCase()))) && m.compatibility >= min;
  });
  async function run() { setBusy(true); setErr(''); try { await Matching.run(resume.id); await reload(); } catch (e) { setErr(errMsg(e)); } finally { setBusy(false); } }
  if (loading) return <Spinner label="Loading matches…" />;
  if (error) return <ErrorBox error={error} onRetry={reload} />;
  if (!matches.length) return <Card className="text-center"><p className="mb-4 text-sm text-muted">Compare your resume with every active job.</p><Btn variant="primary" icon={Play} loading={busy} onClick={run}>Find matching jobs</Btn><div className="mt-3"><ErrorBox error={err} /></div></Card>;
  return (
    <div className="space-y-6">
      <Card className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <div className="relative xl:col-span-2"><Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted" /><input aria-label="Search jobs" className="field !pl-11" placeholder="Search title, company, description…" value={q} onChange={(e) => setQ(e.target.value)} /></div>
        <select aria-label="Role category" className="field" value={cat} onChange={(e) => setCat(e.target.value)}><option value="">All roles</option>{cats.map((c) => <option key={c}>{c}</option>)}</select>
        <select aria-label="Max experience" className="field" value={maxExp} onChange={(e) => setMaxExp(e.target.value)}><option value="">Any experience</option><option value="0">Fresher (0 yrs)</option><option value="1">Up to 1 yr</option><option value="2">Up to 2 yrs</option><option value="4">Up to 4 yrs</option></select>
        <input aria-label="Filter by skill" className="field" placeholder="Filter by skill, e.g. Docker" value={skill} onChange={(e) => setSkill(e.target.value)} />
        <div className="md:col-span-2 xl:col-span-4"><label className="label">Minimum compatibility: <b style={{ color: scoreColor(min) }}>{min}%</b></label><input type="range" min="0" max="90" step="5" value={min} onChange={(e) => setMin(Number(e.target.value))} className="w-full accent-[#7a3cff]" /></div>
        <Btn icon={Play} loading={busy} onClick={run}>Re-run matching</Btn>
      </Card>
      <ErrorBox error={err} />
      <p className="text-sm font-semibold text-muted">{list.length} of {matches.length} jobs · ranked by compatibility</p>
      <div className="space-y-5">{list.map((m) => <JobCard key={m.job.id} m={m} />)}{!list.length && <Card className="text-center text-sm text-muted">No jobs match these filters.</Card>}</div>
    </div>
  );
}
export default function Jobs() { return (<div><PageHeader title="Job matching" subtitle="Every active job ranked by how well your resume fits" /><ResumeGate>{(r) => <Body resume={r} key={r.id} />}</ResumeGate></div>); }
