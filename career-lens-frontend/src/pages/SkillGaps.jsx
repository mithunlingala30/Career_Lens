import { useState } from 'react';
import { Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Lightbulb } from 'lucide-react';
import { Gaps } from '../services/api';
import { Card, Chip, ErrorBox, PALETTE, PageHeader, ProgressBar, ScoreRing, Spinner, Empty, tipStyle } from '../components/ui';
import ResumeGate from '../components/ResumeGate';
import useFetch from '../hooks/useFetch';

function Body({ resume }) {
  const [jobId, setJobId] = useState(null);
  const { data: d, loading, error, reload } = useFetch(() => Gaps.get(resume.id, jobId), [resume.id, jobId]);
  if (loading && !d) return <Spinner label="Analysing skill gaps…" />;
  if (error) return <ErrorBox error={error} onRetry={reload} />;
  if (!d.jobs.length) return <Empty title="Run job matching first" text="Skill gaps are computed per job when your resume is matched." action="Go to job matching" to="/app/jobs" />;
  const job = d.jobs.find((j) => j.id === d.selected_job_id);
  const perJob = d.jobs.slice(0, 8).map((j) => ({ job: j.title, Matched: j.matched, Missing: j.missing }));
  const byArea = Object.entries(d.candidate_skills.reduce((a, s) => ({ ...a, [s.area]: (a[s.area] || 0) + 1 }), {})).map(([area, count]) => ({ area, count }));
  return (
    <div className="space-y-6">
      <Card className="flex flex-wrap items-center gap-4"><label className="label !m-0" htmlFor="gj">Target job</label>
        <select id="gj" className="field !w-auto min-w-[260px] flex-1" value={d.selected_job_id || ''} onChange={(e) => setJobId(Number(e.target.value))}>{d.jobs.map((j) => <option key={j.id} value={j.id}>{j.title} - {j.company} ({Math.round(j.compatibility)}%)</option>)}</select></Card>
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="flex flex-col items-center gap-2"><ScoreRing value={d.coverage} size={150} sub="%" label="Skill coverage" /><p className="text-center text-xs text-muted">Importance-weighted share of {job?.title} requirements you already meet.</p></Card>
        <Card className="lg:col-span-2"><h2 className="mb-3 text-lg font-extrabold">Your skills ({d.candidate_skills.length})</h2><div className="flex flex-wrap gap-2">{d.candidate_skills.map((s) => <Chip key={s.skill} color={d.matched.some((m) => m.skill === s.skill) ? 'green' : 'blue'} title={s.area}>{s.skill}</Chip>)}</div><p className="mt-3 text-xs text-muted">Green = also required by the selected job.</p></Card>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card><h2 className="mb-3 text-lg font-extrabold text-bright-teal">Matched skills ({d.matched.length})</h2><div className="space-y-3">{d.matched.map((m) => <div key={m.skill}><div className="mb-1 flex justify-between text-sm font-bold"><span>{m.skill}</span><span className="text-muted">{m.importance}/5</span></div><ProgressBar value={100} grad="linear-gradient(90deg,#00c4a7,#22c55e)" /></div>)}{!d.matched.length && <span className="text-sm text-muted">No overlap with this job yet.</span>}</div></Card>
        <Card><h2 className="mb-3 text-lg font-extrabold text-bright-pink">Missing skills ({d.missing.length})</h2><div className="space-y-3">{d.missing.map((m) => <div key={m.skill}><div className="mb-1 flex justify-between text-sm font-bold"><span>{m.skill}{m.mandatory && ' ★'}</span><span className="text-muted">{m.importance}/5</span></div><ProgressBar value={m.importance * 20} grad="linear-gradient(90deg,#ff3d95,#ff8a1f)" /></div>)}{!d.missing.length && <span className="text-sm text-muted">Nothing missing - excellent!</span>}</div></Card>
      </div>
      <Card><h2 className="mb-4 flex items-center gap-2 text-lg font-extrabold"><Lightbulb size={20} className="text-bright-orange" />Skill development suggestions</h2>
        <div className="grid gap-4 md:grid-cols-2">{d.missing.slice(0, 6).map((m) => <div key={m.skill} className="neu-inset p-4 text-sm"><Chip color="pink">{m.skill}</Chip><p className="mt-2 text-muted">{m.suggestion}</p></div>)}</div>
        {!!d.learning_areas.length && <div className="mt-5 flex flex-wrap gap-2">{d.learning_areas.map((a) => <Chip key={a.area} color="violet" title={a.tip}>{a.area}: {a.skills.length}</Chip>)}</div>}</Card>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card><h2 className="mb-3 text-lg font-extrabold">Matched vs missing per job</h2><ResponsiveContainer width="100%" height={300}><BarChart data={perJob} layout="vertical" margin={{ left: 30 }}><CartesianGrid strokeDasharray="3 3" stroke="#cdd5ea" /><XAxis type="number" fontSize={11} /><YAxis type="category" dataKey="job" width={120} fontSize={10} /><Tooltip contentStyle={tipStyle} /><Legend wrapperStyle={{ fontSize: 11 }} /><Bar dataKey="Matched" stackId="a" fill="#00c4a7" /><Bar dataKey="Missing" stackId="a" fill="#ff3d95" radius={[0, 8, 8, 0]} /></BarChart></ResponsiveContainer></Card>
        <Card><h2 className="mb-3 text-lg font-extrabold">Most common gaps across all jobs</h2><ResponsiveContainer width="100%" height={300}><BarChart data={d.aggregate_missing.slice(0, 8)} layout="vertical" margin={{ left: 30 }}><CartesianGrid strokeDasharray="3 3" stroke="#cdd5ea" /><XAxis type="number" allowDecimals={false} fontSize={11} /><YAxis type="category" dataKey="skill" width={110} fontSize={11} /><Tooltip contentStyle={tipStyle} /><Bar dataKey="jobs_requiring" name="Jobs requiring" radius={[0, 10, 10, 0]}>{d.aggregate_missing.map((_, i) => <Cell key={i} fill={PALETTE[i % 7]} />)}</Bar></BarChart></ResponsiveContainer></Card>
      </div>
    </div>
  );
}
export default function SkillGaps() { return (<div><PageHeader title="Skill gap analysis" subtitle="What you have, what the job needs, and how to close the distance" /><ResumeGate>{(r) => <Body resume={r} key={r.id} />}</ResumeGate></div>); }
