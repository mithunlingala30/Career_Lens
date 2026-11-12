import { useState } from 'react';
import { Users, FileText, Briefcase, Gauge, Plus, Pencil, Trash2, Wand2, X, Tags, FlaskConical } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Dashboard, Jobs, errMsg } from '../services/api';
import { Btn, Card, Chip, EDU_LEVELS, ErrorBox, Field, Modal, Notice, PALETTE, PageHeader, Spinner, StatCard, fmtDate, tipStyle } from '../components/ui';
import useFetch from '../hooks/useFetch';

const EMPTY = { title: '', company: '', category: '', location: '', employment_type: 'Full-time', salary_range: '', description: '', min_education_level: 2, min_experience_years: 0, is_active: true, requirements: [] };

function JobForm({ initial, categories, onSaved, onClose }) {
  const [j, setJ] = useState(() => structuredClone(initial));
  const [err, setErr] = useState(''); const [busy, setBusy] = useState(false); const [note, setNote] = useState('');
  const set = (k) => (e) => setJ({ ...j, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value });
  const setReq = (i, k, v) => setJ({ ...j, requirements: j.requirements.map((r, x) => (x === i ? { ...r, [k]: v } : r)) });
  async function detect() {
    setErr(''); setNote('');
    try { const r = await Jobs.extractSkills(j.description); setJ({ ...j, requirements: r }); setNote(`${r.length} skills detected from the description - adjust importance as needed.`); } catch (e) { setErr(errMsg(e)); }
  }
  async function submit(e) {
    e.preventDefault(); setErr(''); setBusy(true);
    const body = { ...j, min_education_level: Number(j.min_education_level), min_experience_years: Number(j.min_experience_years), requirements: j.requirements.filter((r) => r.skill_name.trim()).map((r) => ({ skill_name: r.skill_name.trim(), importance: Number(r.importance), is_mandatory: !!r.is_mandatory })) };
    try { j.id ? await Jobs.update(j.id, body) : await Jobs.create(body); onSaved(); } catch (x) { setErr(errMsg(x)); } finally { setBusy(false); }
  }
  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Job title *"><input className="field" required value={j.title} onChange={set('title')} /></Field>
        <Field label="Company"><input className="field" value={j.company} onChange={set('company')} /></Field>
        <Field label="Career category *"><input className="field" required list="cats" value={j.category} onChange={set('category')} /><datalist id="cats">{categories.map((c) => <option key={c} value={c} />)}</datalist></Field>
        <Field label="Location"><input className="field" value={j.location} onChange={set('location')} /></Field>
        <Field label="Minimum education"><select className="field" value={j.min_education_level} onChange={set('min_education_level')}>{EDU_LEVELS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></Field>
        <Field label="Minimum experience (years)"><input className="field" type="number" min="0" step="0.5" value={j.min_experience_years} onChange={set('min_experience_years')} /></Field>
        <Field label="Salary range"><input className="field" value={j.salary_range} onChange={set('salary_range')} placeholder="6-12 LPA" /></Field>
        <label className="flex items-center gap-3 pt-6 text-sm font-bold"><input type="checkbox" className="h-5 w-5 accent-[#7a3cff]" checked={j.is_active} onChange={set('is_active')} />Active (visible to candidates)</label>
      </div>
      <Field label="Job description * (mention required skills)"><textarea className="field" rows={4} required minLength={10} value={j.description} onChange={set('description')} /></Field>
      <div><div className="mb-2 flex items-center justify-between"><span className="label !m-0">Required skills & importance</span><div className="flex gap-2"><Btn size="sm" type="button" icon={Wand2} onClick={detect} disabled={j.description.length < 10}>Extract from description</Btn><Btn size="sm" type="button" icon={Plus} onClick={() => setJ({ ...j, requirements: [...j.requirements, { skill_name: '', importance: 3, is_mandatory: false }] })}>Add</Btn></div></div>
        <div className="space-y-2">{j.requirements.map((r, i) => (
          <div key={i} className="flex flex-wrap items-center gap-2"><input className="field !w-auto min-w-[140px] flex-1" aria-label="Skill name" value={r.skill_name} onChange={(e) => setReq(i, 'skill_name', e.target.value)} placeholder="Skill" />
            <select className="field !w-24" aria-label="Importance" value={r.importance} onChange={(e) => setReq(i, 'importance', e.target.value)}>{[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n}/5</option>)}</select>
            <label className="flex items-center gap-1 text-xs font-bold"><input type="checkbox" className="accent-[#ff3d95]" checked={r.is_mandatory} onChange={(e) => setReq(i, 'is_mandatory', e.target.checked)} />Must</label>
            <button type="button" aria-label="Remove skill" className="btn btn-sm !p-2" onClick={() => setJ({ ...j, requirements: j.requirements.filter((_, x) => x !== i) })}><X size={14} /></button></div>))}
          {!j.requirements.length && <p className="text-xs text-muted">Leave empty to auto-detect skills from the description when saving.</p>}</div></div>
      {note && <Notice tone="green">{note}</Notice>}<ErrorBox error={err} />
      <div className="flex gap-3"><Btn variant="primary" type="submit" loading={busy}>{j.id ? 'Save job' : 'Create job'}</Btn><Btn type="button" onClick={onClose}>Cancel</Btn></div>
    </form>
  );
}

export default function AdminDashboard() {
  const dash = useFetch(Dashboard.admin, []);
  const jobs = useFetch(() => Jobs.list(), []);
  const [tab, setTab] = useState('overview');
  const [edit, setEdit] = useState(null);
  const [err, setErr] = useState(''); const [rename, setRename] = useState({ old: '', neu: '' }); const [msg, setMsg] = useState('');
  const cats = [...new Set((jobs.data || []).map((j) => j.category))].sort();
  const refresh = () => { dash.reload(); jobs.reload(); };
  async function del(j) { if (!window.confirm(`Delete "${j.title}"? Related matches and evaluations are removed.`)) return; try { await Jobs.remove(j.id); refresh(); } catch (e) { setErr(errMsg(e)); } }
  async function ren(e) { e.preventDefault(); setErr(''); setMsg(''); try { const r = await Jobs.renameCategory(rename.old, rename.neu); setMsg(`Renamed - ${r.updated_jobs} jobs updated.`); setRename({ old: '', neu: '' }); refresh(); } catch (x) { setErr(errMsg(x)); } }

  if (dash.loading && !dash.data) return <Spinner label="Loading admin dashboard…" />;
  if (dash.error) return <ErrorBox error={dash.error} onRetry={dash.reload} />;
  const d = dash.data, s = d.stats, v = d.validation;
  return (
    <div className="space-y-6">
      <PageHeader title="Admin dashboard" subtitle="Platform statistics, job opportunities and requirements"><Btn variant="primary" icon={Plus} onClick={() => setEdit({ ...EMPTY })}>Add new job</Btn></PageHeader>
      <div className="neu-inset inline-flex gap-1 p-1" role="tablist">{[['overview', 'Overview'], ['jobs', 'Jobs & requirements'], ['categories', 'Categories'], ['users', 'Users']].map(([k, l]) => <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)} className="rounded-xl px-4 py-2 text-sm font-bold" style={tab === k ? { background: 'linear-gradient(135deg,#2f6bff,#7a3cff)', color: '#fff' } : { color: '#5b6892' }}>{l}</button>)}</div>
      <ErrorBox error={err} />{msg && <Notice tone="green">{msg}</Notice>}

      {tab === 'overview' && <>
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4"><StatCard icon={Users} label="Registered candidates" value={s.candidates} grad="blue" /><StatCard icon={FileText} label="Uploaded resumes" value={s.resumes} grad="pink" /><StatCard icon={Briefcase} label="Job listings" value={s.jobs} hint={`${s.active_jobs} active`} grad="teal" /><StatCard icon={Gauge} label="Avg. evaluation score" value={s.avg_score} grad="orange" /></div>
        <div className="grid gap-6 xl:grid-cols-3">
          <Card className="xl:col-span-2"><h2 className="mb-3 text-lg font-extrabold">Resume score distribution</h2><ResponsiveContainer width="100%" height={260}><BarChart data={d.score_distribution}><CartesianGrid strokeDasharray="3 3" stroke="#cdd5ea" /><XAxis dataKey="range" fontSize={11} /><YAxis allowDecimals={false} fontSize={11} /><Tooltip contentStyle={tipStyle} /><Bar dataKey="count" name="Resumes" radius={[10, 10, 0, 0]}>{d.score_distribution.map((_, i) => <Cell key={i} fill={PALETTE[i % 7]} />)}</Bar></BarChart></ResponsiveContainer></Card>
          <Card><h2 className="mb-3 text-lg font-extrabold">Jobs by category</h2><ResponsiveContainer width="100%" height={260}><PieChart><Pie data={d.jobs_by_category} dataKey="count" nameKey="category" innerRadius={50} outerRadius={90} paddingAngle={3}>{d.jobs_by_category.map((_, i) => <Cell key={i} fill={PALETTE[i % 7]} />)}</Pie><Tooltip contentStyle={tipStyle} /></PieChart></ResponsiveContainer></Card>
        </div>
        <div className="grid gap-6 xl:grid-cols-2">
          <Card><h2 className="mb-3 text-lg font-extrabold">Most common skill gaps</h2>{d.top_missing_skills.length ? <div className="flex flex-wrap gap-2">{d.top_missing_skills.map((m) => <Chip key={m.skill} color="pink">{m.skill} · {m.count}</Chip>)}</div> : <p className="text-sm text-muted">Appears once candidates are matched.</p>}</Card>
          <Card><h2 className="mb-2 flex items-center gap-2 text-lg font-extrabold"><FlaskConical size={18} className="text-bright-violet" />Algorithm validation</h2><p className="text-sm text-muted">Proposed accuracy <b className="text-navy">{(v.proposed_accuracy * 100).toFixed(1)}%</b> vs keyword <b className="text-navy">{(v.baseline_accuracy * 100).toFixed(1)}%</b> on {v.n} cases; paired t-test p = <b className="text-navy">{v.p_value < 0.001 ? '< 0.001' : v.p_value.toFixed(4)}</b>.</p><p className="mt-2 text-sm font-bold">{v.conclusion}</p></Card>
        </div></>}

      {tab === 'jobs' && (jobs.loading ? <Spinner /> : <Card className="overflow-x-auto !p-2"><table className="table-neu w-full min-w-[760px]"><thead><tr><th>Job</th><th>Category</th><th>Requirements</th><th>Edu / Exp</th><th>Status</th><th className="text-right">Actions</th></tr></thead>
        <tbody>{jobs.data.map((j) => <tr key={j.id}><td><b>{j.title}</b><div className="text-xs text-muted">{j.company} · {j.location}</div></td><td><Chip color="violet">{j.category}</Chip></td>
          <td className="max-w-[280px]"><div className="flex flex-wrap gap-1">{j.requirements.slice(0, 5).map((r) => <Chip key={r.skill_name} color="blue">{r.skill_name} {r.importance}</Chip>)}{j.requirements.length > 5 && <span className="text-xs text-muted">+{j.requirements.length - 5}</span>}</div></td>
          <td className="whitespace-nowrap text-xs">{EDU_LEVELS[j.min_education_level][1]} · {j.min_experience_years}y</td><td><Chip color={j.is_active ? 'green' : 'gray'}>{j.is_active ? 'Active' : 'Hidden'}</Chip></td>
          <td><div className="flex justify-end gap-2"><Btn size="sm" icon={Pencil} onClick={() => setEdit(structuredClone(j))} aria-label={`Edit ${j.title}`}>Edit</Btn><Btn size="sm" variant="pink" icon={Trash2} onClick={() => del(j)} aria-label={`Delete ${j.title}`}>Delete</Btn></div></td></tr>)}</tbody></table></Card>)}

      {tab === 'categories' && <div className="grid gap-6 lg:grid-cols-2"><Card><h2 className="mb-4 flex items-center gap-2 text-lg font-extrabold"><Tags size={18} className="text-bright-violet" />Career categories</h2><ul className="space-y-2">{d.jobs_by_category.map((c) => <li key={c.category} className="neu-flat flex items-center justify-between px-4 py-3 text-sm font-bold">{c.category}<Chip color="blue">{c.count} jobs</Chip></li>)}</ul></Card>
        <Card><h2 className="mb-4 text-lg font-extrabold">Rename a category</h2><form onSubmit={ren} className="space-y-4"><Field label="Existing category"><select className="field" required value={rename.old} onChange={(e) => setRename({ ...rename, old: e.target.value })}><option value="">Select…</option>{d.jobs_by_category.map((c) => <option key={c.category}>{c.category}</option>)}</select></Field>
          <Field label="New name"><input className="field" required minLength={2} value={rename.neu} onChange={(e) => setRename({ ...rename, neu: e.target.value })} /></Field><Btn variant="primary" type="submit">Rename</Btn><p className="text-xs text-muted">Create new categories by typing a new name in the job form.</p></form></Card></div>}

      {tab === 'users' && <Card className="overflow-x-auto !p-2"><table className="table-neu w-full min-w-[620px]"><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Resumes</th><th>Joined</th></tr></thead><tbody>{d.users.map((u) => <tr key={u.id}><td><b>{u.full_name}</b></td><td>{u.email}</td><td><Chip color={u.role === 'admin' ? 'pink' : 'blue'}>{u.role}</Chip></td><td>{u.resumes}</td><td className="text-muted">{fmtDate(u.created_at)}</td></tr>)}</tbody></table></Card>}

      <Modal open={!!edit} onClose={() => setEdit(null)} title={edit?.id ? 'Edit job' : 'Add new job'} wide>{edit && <JobForm initial={edit} categories={cats} onClose={() => setEdit(null)} onSaved={() => { setEdit(null); refresh(); }} />}</Modal>
    </div>
  );
}
