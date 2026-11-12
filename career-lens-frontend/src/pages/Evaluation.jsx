import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Download, Play, CheckCircle2, XCircle, GraduationCap, Briefcase, FlaskConical } from 'lucide-react';
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Evaluation as API, Matching, Reports, errMsg } from '../services/api';
import { Btn, Card, Chip, ErrorBox, PageHeader, PALETTE, ProgressBar, ScoreRing, Spinner, fmtDate, tipStyle } from '../components/ui';
import ResumeGate from '../components/ResumeGate';
import useFetch from '../hooks/useFetch';

const pct = (v) => `${(v * 100).toFixed(1)}%`;

function Validation() {
  const { data: v, loading } = useFetch(API.validation, []);
  if (loading || !v) return null;
  const t = v.paired_t_test, m = v.mcnemar_test;
  return (
    <Card>
      <h2 className="mb-1 flex items-center gap-2 text-lg font-extrabold"><FlaskConical size={18} className="text-bright-violet" />Algorithm validation: hypothesis testing</h2>
      <p className="mb-4 text-sm text-muted">Proposed matcher vs. basic keyword matching on {v.n} held-out labelled cases (both calibrated identically).</p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[['Proposed accuracy', pct(v.proposed.accuracy), '#2f6bff'], ['Keyword accuracy', pct(v.baseline.accuracy), '#ff8a1f'], ['Paired t-test p', t.p_value < 0.001 ? '< 0.001' : t.p_value.toFixed(4), t.significant ? '#00c4a7' : '#ff3d95'], ["McNemar p", m.p_value < 0.001 ? '< 0.001' : m.p_value.toFixed(4), m.significant ? '#00c4a7' : '#ff8a1f']].map(([l, val, c]) =>
          <div key={l} className="neu-inset p-4 text-center"><div className="text-xs font-bold text-muted">{l}</div><div className="font-display text-2xl font-extrabold" style={{ color: c }}>{val}</div></div>)}
      </div>
      <p className="mt-4 text-sm"><b>{v.conclusion}</b> Brier error {v.proposed.brier.toFixed(3)} vs {v.baseline.brier.toFixed(3)}; Cohen's d<sub>z</sub> = {t.cohens_dz.toFixed(2)}. Validation cases are simulated (see README).</p>
    </Card>
  );
}

function Detail({ ev, onDownload, onRerun, busy }) {
  const g = ev.gaussian;
  const curve = g.curve.map((p) => ({ x: p.x, density: +(p.density * 100).toFixed(3) }));
  return (
    <div className="space-y-6">
      <Card className="flex flex-wrap items-center justify-around gap-8">
        <ScoreRing value={ev.resume_score} size={170} label="Overall resume score / 100" />
        <ScoreRing value={ev.compatibility} size={170} sub="%" color="#7a3cff" label={`Compatibility: ${ev.job_title}`} />
        <div className="max-w-xs space-y-2 text-sm"><Chip color="violet">{g.band}</Chip>
          <p className="text-muted">Your resume scores higher than <b className="text-navy">{g.percentile.toFixed(0)}%</b> of the {g.source}. z = {g.z_score.toFixed(2)}.</p>
          <div className="flex gap-2 pt-2"><Btn variant="primary" size="sm" icon={Download} onClick={onDownload}>PDF report</Btn><Btn size="sm" icon={Play} loading={busy} onClick={onRerun}>Re-evaluate</Btn></div>
          <p className="text-xs text-muted">Evaluated {fmtDate(ev.evaluated_at)}</p></div>
      </Card>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card><h3 className="mb-3 flex items-center gap-2 font-extrabold"><CheckCircle2 className="text-bright-teal" size={18} />Matched skills ({ev.matched_skills.length})</h3>
          <div className="flex flex-wrap gap-2">{ev.matched_skills.map((s) => <Chip key={s.skill} color="green" title={s.evidence}>{s.skill} · {s.importance}/5</Chip>)}{!ev.matched_skills.length && <span className="text-sm text-muted">None yet.</span>}</div></Card>
        <Card><h3 className="mb-3 flex items-center gap-2 font-extrabold"><XCircle className="text-bright-pink" size={18} />Missing skills ({ev.missing_skills.length})</h3>
          <div className="flex flex-wrap gap-2">{ev.missing_skills.map((s) => <Chip key={s.skill} color="pink">{s.skill} · {s.importance}/5{s.mandatory && ' ★'}</Chip>)}{!ev.missing_skills.length && <span className="text-sm text-muted">You cover every requirement.</span>}</div></Card>
        {[[GraduationCap, 'Education match', ev.education_match, `Required: ${ev.education_match.required_label}`, `You: ${ev.education_match.candidate_label}`],
          [Briefcase, 'Experience match', ev.experience_match, `Required: ${ev.experience_match.required_years} yrs`, `You: ${ev.experience_match.candidate_years} yrs`]].map(([Icon, t, m, a, b]) =>
          <Card key={t}><h3 className="mb-3 flex items-center gap-2 font-extrabold"><Icon size={18} className="text-bright-violet" />{t}</h3><div className="mb-2 flex justify-between text-sm"><span>{a}</span><b>{b}</b></div><ProgressBar value={m.score} grad={m.met ? 'linear-gradient(90deg,#00c4a7,#22c55e)' : 'linear-gradient(90deg,#ff8a1f,#ff3d95)'} /><p className="mt-2 text-xs text-muted">{m.met ? 'Requirement met' : `Partially met (${m.score}%)`}</p></Card>)}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card><h3 className="mb-3 font-extrabold">Compatibility score breakdown</h3>
          <ResponsiveContainer width="100%" height={260}><BarChart data={ev.score_components} layout="vertical" margin={{ left: 20 }}><CartesianGrid strokeDasharray="3 3" stroke="#cdd5ea" /><XAxis type="number" domain={[0, 100]} fontSize={11} /><YAxis type="category" dataKey="name" width={140} fontSize={11} /><Tooltip contentStyle={tipStyle} formatter={(v, n, p) => [`${v}% (weight ${p.payload.weight * 100}%)`, 'Score']} />
            <Bar dataKey="score" radius={[0, 10, 10, 0]}>{ev.score_components.map((_, i) => <Cell key={i} fill={PALETTE[i]} />)}</Bar></BarChart></ResponsiveContainer></Card>
        <Card><h3 className="mb-3 font-extrabold">Resume quality breakdown</h3>
          <div className="space-y-3">{ev.resume_breakdown.map((b, i) => <div key={b.name}><div className="mb-1 flex justify-between text-xs font-bold text-muted"><span>{b.name}</span><span>{b.score}/{b.max}</span></div><ProgressBar value={(b.score / b.max) * 100} grad={`linear-gradient(90deg,${PALETTE[i]},${PALETTE[(i + 1) % 7]})`} /></div>)}</div></Card>
      </div>
      <Card><h3 className="mb-1 font-extrabold">Gaussian analysis: your score vs. the cohort</h3>
        <p className="mb-3 text-xs text-muted">Reference N(μ={g.mean.toFixed(1)}, σ={g.std.toFixed(1)}) from {g.source}. Shapiro-Wilk p = {g.shapiro_p == null ? 'n/a' : g.shapiro_p.toFixed(3)} ({g.normality_ok ? 'normal assumption holds' : 'approximation only - empirical percentile ' + g.empirical_percentile.toFixed(0)}).</p>
        <ResponsiveContainer width="100%" height={220}><AreaChart data={curve}><defs><linearGradient id="bell" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7a3cff" stopOpacity={.55} /><stop offset="1" stopColor="#2f6bff" stopOpacity={.05} /></linearGradient></defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#cdd5ea" /><XAxis type="number" dataKey="x" domain={[0, 100]} fontSize={11} /><YAxis hide /><Tooltip contentStyle={tipStyle} formatter={(v) => [v, 'density']} />
          <Area type="monotone" dataKey="density" stroke="#7a3cff" strokeWidth={3} fill="url(#bell)" /><ReferenceLine x={g.score} stroke="#ff3d95" strokeWidth={3} label={{ value: `You: ${g.score}`, fill: '#ff3d95', fontSize: 12, position: 'top' }} /><ReferenceLine x={g.mean} stroke="#00c4a7" strokeDasharray="5 4" label={{ value: 'Mean', fill: '#00a98f', fontSize: 11, position: 'insideTopRight' }} /></AreaChart></ResponsiveContainer></Card>
      <Card><h3 className="mb-4 font-extrabold">How the mathematics scored this match</h3>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="neu-inset p-4 text-sm"><b className="text-bright-blue">Inner product</b><p className="mt-2 text-muted">⟨c, j⟩ = <b className="text-navy">{ev.inner_product.inner_product}</b> of max {ev.inner_product.max_inner_product}; coverage {pct(ev.inner_product.coverage)}, cosine {pct(ev.inner_product.cosine)}.</p></div>
          <div className="neu-inset p-4 text-sm"><b className="text-bright-pink">Bayes' theorem</b><p className="mt-2 text-muted">Prior {pct(ev.bayes.prior)} → posterior <b className="text-navy">{pct(ev.bayes.posterior)}</b> (Bayes factor {ev.bayes.bayes_factor.toFixed(1)}).</p></div>
          <div className="neu-inset p-4 text-sm"><b className="text-bright-teal">Conditional probability</b><p className="mt-2 text-muted">P(suitable | {ev.conditional.coverage_bin} coverage, education, experience) = <b className="text-navy">{pct(ev.conditional.p_conditional)}</b> from {ev.conditional.cell_support} similar cases.</p></div>
          <div className="neu-inset p-4 text-sm"><b className="text-bright-violet">SVD latent fit</b><p className="mt-2 text-muted">Rank-{ev.svd.k} similarity <b className="text-navy">{pct(ev.svd.similarity)}</b>; factors explain {pct(ev.svd.cumulative_variance)} of variance.</p></div>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">{ev.svd.factors.map((f) => <Chip key={f.factor} color="violet" title={`Explained variance ${pct(f.explained_variance)}`}>Factor {f.factor}: {f.top_skills.slice(0, 3).join(', ')}</Chip>)}</div></Card>
    </div>
  );
}

function Body({ resume }) {
  const [sp, setSp] = useSearchParams();
  const jobId = Number(sp.get('job')) || null;
  const jobs = useFetch(() => Matching.get(resume.id), [resume.id]);
  const matches = jobs.data?.matches || [];
  useEffect(() => { if (!jobId && matches.length) setSp({ job: matches[0].job.id }, { replace: true }); }, [jobId, matches, setSp]);
  const ev = useFetch(() => API.get(resume.id, jobId), [resume.id, jobId], !!jobId);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');
  async function run() { setBusy(true); setErr(''); try { await API.run(resume.id, jobId); await ev.reload(); } catch (e) { setErr(errMsg(e)); } finally { setBusy(false); } }

  if (jobs.loading) return <Spinner label="Loading jobs…" />;
  if (!matches.length) return <Card className="text-center"><p className="mb-4 text-sm text-muted">No job matches calculated yet.</p><Btn variant="primary" icon={Play} loading={busy} onClick={async () => { setBusy(true); try { await Matching.run(resume.id); await jobs.reload(); } catch (e) { setErr(errMsg(e)); } finally { setBusy(false); } }}>Run matching</Btn><div className="mt-3"><ErrorBox error={err} /></div></Card>;
  return (
    <div className="space-y-6">
      <Card className="flex flex-wrap items-center gap-4"><label className="label !m-0" htmlFor="jobsel">Evaluate against</label>
        <select id="jobsel" className="field !w-auto min-w-[260px] flex-1" value={jobId || ''} onChange={(e) => setSp({ job: e.target.value })}>{matches.map((m) => <option key={m.job.id} value={m.job.id}>{m.job.title} - {m.job.company} ({Math.round(m.compatibility)}%)</option>)}</select></Card>
      <ErrorBox error={err} />
      {ev.loading ? <Spinner label="Loading evaluation…" /> : ev.status === 404 ? <Card className="text-center"><p className="mb-4 text-sm text-muted">This job has not been evaluated yet.</p><Btn variant="primary" icon={Play} loading={busy} onClick={run}>Run evaluation</Btn></Card>
        : ev.error ? <ErrorBox error={ev.error} onRetry={ev.reload} />
        : ev.data && <Detail ev={ev.data} busy={busy} onRerun={run} onDownload={() => Reports.pdf(ev.data.id).catch((e) => setErr(errMsg(e)))} />}
      <Validation />
    </div>
  );
}

export default function Evaluation() {
  return (<div><PageHeader title="Resume evaluation" subtitle="Scores, matched skills and the probability maths behind them" /><ResumeGate>{(r) => <Body resume={r} key={r.id} />}</ResumeGate></div>);
}
