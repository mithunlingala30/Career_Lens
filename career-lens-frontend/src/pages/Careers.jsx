import { useState } from 'react';
import { Play, TrendingUp, Timer } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Recs, errMsg } from '../services/api';
import { Btn, Card, Chip, ErrorBox, PALETTE, PageHeader, ProgressBar, ScoreRing, Spinner, tipStyle } from '../components/ui';
import ResumeGate from '../components/ResumeGate';
import useFetch from '../hooks/useFetch';

function Ladder({ ladder, current }) {
  return (
    <ol className="flex flex-wrap items-center gap-2" aria-label="Career progression">{ladder.map((t, i) => (
      <li key={t} className="flex items-center gap-2"><span className="rounded-2xl px-4 py-2 text-xs font-bold" style={i === current ? { background: 'linear-gradient(135deg,#2f6bff,#7a3cff)', color: '#fff', boxShadow: '4px 6px 14px rgba(47,107,255,.4)' } : i < current ? { color: '#009e87' } : { color: '#8d98bb' }}>{i < current ? '✓ ' : ''}{t}{i === current && ' (you are here)'}</span>{i < ladder.length - 1 && <span className="text-muted">›</span>}</li>))}</ol>
  );
}

function RecCard({ r }) {
  const mk = r.progression.markov;
  const data = Object.entries(mk.distribution).map(([t, d]) => ({ month: `${t} mo`, ...Object.fromEntries(mk.states.map((s, i) => [s, +(d[i] * 100).toFixed(1)])) }));
  return (
    <Card>
      <div className="flex flex-wrap items-center gap-6">
        <ScoreRing value={r.suitability} size={110} sub="%" label="Suitability" color="#7a3cff" /><ScoreRing value={r.readiness} size={110} sub="%" label="Readiness" color="#00c4a7" />
        <div className="min-w-[200px] flex-1"><div className="flex flex-wrap items-center gap-2"><h2 className="text-xl font-extrabold">{r.category}</h2><Chip color="violet">#{r.rank}</Chip><Chip color="orange">{mk.current_state_name}</Chip></div>
          <p className="mt-1 text-sm text-muted">Best-fit roles: {r.progression.roles.sort((a, b) => b.compatibility - a.compatibility).slice(0, 3).map((x) => `${x.title} (${Math.round(x.compatibility)}%)`).join(', ')}</p>
          {mk.expected_months_to_target != null && <p className="mt-2 flex items-center gap-2 text-sm font-bold text-bright-blue"><Timer size={16} />≈ {mk.expected_months_to_target} months to reach {mk.target_state_name}</p>}</div>
      </div>
      <div className="mt-6"><h3 className="mb-2 text-sm font-extrabold">Career progression</h3><Ladder ladder={r.progression.ladder} current={r.progression.current_rung} /></div>
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div><h3 className="mb-2 text-sm font-extrabold text-bright-teal">Existing skills ({r.existing_skills.length})</h3><div className="flex flex-wrap gap-2">{r.existing_skills.map((s) => <Chip key={s} color="green">{s}</Chip>)}{!r.existing_skills.length && <span className="text-sm text-muted">None of the core skills yet.</span>}</div></div>
        <div><h3 className="mb-2 text-sm font-extrabold text-bright-pink">Missing skills ({r.missing_skills.length})</h3><div className="flex flex-wrap gap-2">{r.missing_skills.map((s) => <Chip key={s.skill} color="pink">{s.skill}</Chip>)}</div></div>
        <div><h3 className="mb-2 text-sm font-extrabold">Required skills</h3><div className="space-y-1.5">{r.required_skills.slice(0, 6).map((s) => <div key={s.skill} className="flex items-center gap-2 text-xs font-bold"><span className="w-28 truncate">{s.skill}</span><div className="flex-1"><ProgressBar value={s.importance * 20} grad={s.has ? 'linear-gradient(90deg,#00c4a7,#22c55e)' : 'linear-gradient(90deg,#ff3d95,#ff8a1f)'} /></div></div>)}</div></div>
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div><h3 className="mb-2 flex items-center gap-2 text-sm font-extrabold"><TrendingUp size={16} className="text-bright-violet" />Markov forecast: stage probabilities (%)</h3>
          <ResponsiveContainer width="100%" height={230}><BarChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#cdd5ea" /><XAxis dataKey="month" fontSize={11} /><YAxis domain={[0, 100]} fontSize={11} /><Tooltip contentStyle={tipStyle} /><Legend wrapperStyle={{ fontSize: 11 }} />{mk.states.map((s, i) => <Bar key={s} dataKey={s} stackId="a" fill={PALETTE[i]} />)}</BarChart></ResponsiveContainer>
          <p className="mt-1 text-xs text-muted">P(reach {mk.target_state_name}): {Object.entries(mk.probability_reach_target).map(([t, p]) => `${t}mo ${(p * 100).toFixed(0)}%`).join(' · ')}</p></div>
        <div><h3 className="mb-2 text-sm font-extrabold">Suggested learning areas</h3>
          <div className="space-y-3">{r.learning_areas.map((a) => <div key={a.area} className="neu-inset p-3 text-sm"><b>{a.area}</b>: {a.skills.join(', ')}<div className="mt-1 text-xs text-muted">Tip: {a.tip}.</div></div>)}{!r.learning_areas.length && <span className="text-sm text-muted">No gaps - focus on depth and projects.</span>}</div>
          <h3 className="mb-2 mt-5 text-sm font-extrabold">Personalised development plan</h3><ul className="list-disc space-y-1 pl-5 text-sm text-muted">{r.progression.development_suggestions.map((t, i) => <li key={i}>{t}</li>)}</ul></div>
      </div>
    </Card>
  );
}

function Body({ resume }) {
  const { data, loading, error, reload } = useFetch(() => Recs.get(resume.id), [resume.id]);
  const [busy, setBusy] = useState(false); const [err, setErr] = useState('');
  async function run() { setBusy(true); setErr(''); try { await Recs.run(resume.id); await reload(); } catch (e) { setErr(errMsg(e)); } finally { setBusy(false); } }
  if (loading) return <Spinner label="Loading recommendations…" />;
  if (error) return <ErrorBox error={error} onRetry={reload} />;
  const recs = data.recommendations;
  return (
    <div className="space-y-6"><div className="flex justify-end"><Btn variant="primary" icon={Play} loading={busy} onClick={run}>{recs.length ? 'Refresh recommendations' : 'Generate recommendations'}</Btn></div>
      <ErrorBox error={err} />{recs.map((r) => <RecCard key={r.id} r={r} />)}
      {!recs.length && <Card className="text-center text-sm text-muted">No recommendations yet. Generate them to see suitable career paths.</Card>}</div>
  );
}
export default function Careers() { return (<div><PageHeader title="Career recommendations" subtitle="Where your skills fit best, and how long it may take to level up" /><ResumeGate>{(r) => <Body resume={r} key={r.id} />}</ResumeGate></div>); }
