import { Link } from 'react-router-dom';
import { FileText, Gauge, Briefcase, Rocket, ArrowRight } from 'lucide-react';
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Dashboard as API } from '../services/api';
import { Card, Chip, Empty, ErrorBox, PageHeader, PALETTE, ProgressBar, ScoreRing, Spinner, StatCard, fmtDate, tipStyle, scoreColor } from '../components/ui';
import useFetch from '../hooks/useFetch';

const EV = { upload: ['blue', 'Upload'], matching: ['violet', 'Matching'], evaluation: ['green', 'Evaluation'], recommendation: ['orange', 'Careers'] };

export default function Dashboard() {
  const { data: d, loading, error, reload } = useFetch(API.candidate, []);
  if (loading) return <Spinner label="Loading your dashboard…" />;
  if (error) return <ErrorBox error={error} onRetry={reload} />;
  const s = d.stats;
  if (!s.resumes) return <><PageHeader title="Dashboard" subtitle="Your career readiness at a glance" /><Empty title="Let's analyse your first resume" text="Upload a resume and this dashboard fills with scores, matches and recommendations calculated from your data." action="Upload resume" to="/app/upload" /></>;
  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard" subtitle={d.latest_resume ? `Based on ${d.latest_resume.name}` : ''}><Link to="/app/upload" className="btn btn-primary">Upload new resume</Link></PageHeader>
      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={FileText} label="Resumes uploaded" value={s.resumes} grad="blue" />
        <StatCard icon={Gauge} label="Avg. resume score" value={`${s.avg_score}/100`} grad="pink" />
        <StatCard icon={Briefcase} label="Matching jobs (50%+)" value={s.matching_jobs} grad="teal" hint={s.top_job ? `Top: ${s.top_job.title}` : ''} />
        <StatCard icon={Rocket} label="Career readiness" value={`${Math.round(s.readiness)}%`} grad="orange" />
      </div>
      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2"><h2 className="mb-4 text-lg font-extrabold">Score trend</h2>
          {d.charts.score_trend.length ? <ResponsiveContainer width="100%" height={260}><AreaChart data={d.charts.score_trend}>
            <defs><linearGradient id="g1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#2f6bff" stopOpacity={.5} /><stop offset="1" stopColor="#2f6bff" stopOpacity={0} /></linearGradient><linearGradient id="g2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#ff3d95" stopOpacity={.45} /><stop offset="1" stopColor="#ff3d95" stopOpacity={0} /></linearGradient></defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#cdd5ea" /><XAxis dataKey="date" fontSize={11} /><YAxis domain={[0, 100]} fontSize={11} /><Tooltip contentStyle={tipStyle} />
            <Area type="monotone" dataKey="resume_score" name="Resume score" stroke="#2f6bff" strokeWidth={3} fill="url(#g1)" />
            <Area type="monotone" dataKey="compatibility" name="Top job match" stroke="#ff3d95" strokeWidth={3} fill="url(#g2)" /></AreaChart></ResponsiveContainer> : <p className="text-sm text-muted">Run an evaluation to see your trend.</p>}</Card>
        <Card className="flex flex-col items-center justify-center gap-3"><h2 className="self-start text-lg font-extrabold">Career readiness</h2><ScoreRing value={s.readiness} size={170} sub="%" />
          <p className="text-center text-xs text-muted">Weighted blend of skill coverage and Bayes suitability for your best-fit career.</p></Card>
      </div>
      <div className="grid gap-6 xl:grid-cols-2">
        <Card><h2 className="mb-4 text-lg font-extrabold">Compatibility by job</h2>
          {d.charts.job_compat.length ? <ResponsiveContainer width="100%" height={300}><BarChart data={d.charts.job_compat} layout="vertical" margin={{ left: 30 }}><CartesianGrid strokeDasharray="3 3" stroke="#cdd5ea" /><XAxis type="number" domain={[0, 100]} fontSize={11} /><YAxis type="category" dataKey="job" width={130} fontSize={11} /><Tooltip contentStyle={tipStyle} />
            <Bar dataKey="compatibility" radius={[0, 10, 10, 0]}>{d.charts.job_compat.map((x, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} />)}</Bar></BarChart></ResponsiveContainer> : <p className="text-sm text-muted">No matches yet.</p>}</Card>
        <Card><h2 className="mb-4 text-lg font-extrabold">Skills by area</h2>
          {d.charts.skills_by_area.length ? <ResponsiveContainer width="100%" height={300}><RadarChart data={d.charts.skills_by_area}><PolarGrid stroke="#cdd5ea" /><PolarAngleAxis dataKey="area" fontSize={10} /><Radar dataKey="count" name="Skills" stroke="#7a3cff" fill="#7a3cff" fillOpacity={.35} strokeWidth={2} /><Tooltip contentStyle={tipStyle} /></RadarChart></ResponsiveContainer> : <p className="text-sm text-muted">No skills detected.</p>}</Card>
      </div>
      <div className="grid gap-6 xl:grid-cols-3">
        <Card><div className="mb-4 flex items-center justify-between"><h2 className="text-lg font-extrabold">Recommended roles</h2><Link to="/app/careers" className="text-xs font-bold text-bright-blue">View all <ArrowRight size={12} className="inline" /></Link></div>
          {d.recommended_roles.length ? <ul className="space-y-4">{d.recommended_roles.map((r) => <li key={r.category}><div className="mb-1 flex justify-between text-sm font-bold"><span>{r.category}</span><span style={{ color: scoreColor(r.suitability) }}>{Math.round(r.suitability)}%</span></div><ProgressBar value={r.suitability} /></li>)}</ul> : <p className="text-sm text-muted">Run career recommendations from the Careers page.</p>}</Card>
        <Card><div className="mb-4 flex items-center justify-between"><h2 className="text-lg font-extrabold">Skill gap summary</h2><Link to="/app/skill-gaps" className="text-xs font-bold text-bright-blue">Details <ArrowRight size={12} className="inline" /></Link></div>
          {d.skill_gap_summary.length ? <div className="flex flex-wrap gap-2">{d.skill_gap_summary.map((g) => <Chip key={g.skill} color="pink" title={`Required by ${g.jobs_requiring} jobs`}>{g.skill} · {g.jobs_requiring}</Chip>)}</div> : <p className="text-sm text-muted">No gaps found yet.</p>}</Card>
        <Card><h2 className="mb-4 text-lg font-extrabold">Recent evaluations</h2>
          <ul className="space-y-3">{d.recent.map((h) => <li key={h.id} className="flex items-start gap-3 text-sm"><Chip color={EV[h.event_type][0]}>{EV[h.event_type][1]}</Chip><div className="min-w-0"><div className="truncate font-semibold">{h.title}</div><div className="text-xs text-muted">{fmtDate(h.created_at)}</div></div></li>)}</ul></Card>
      </div>
    </div>
  );
}
