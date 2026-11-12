import { useState } from 'react';
import { Plus, Trash2, Save, Pencil, Mail, Phone, MapPin, GraduationCap, Briefcase, Award, FolderGit2, Sparkles, X } from 'lucide-react';
import { errMsg } from '../services/api';
import { Btn, Card, Chip, EDU_LEVELS, ErrorBox, Field } from './ui';

const blank = { education: { degree: '', field_of_study: '', institution: '', start_year: '', end_year: '', grade: '', level: 2 }, experience: { title: '', company: '', start_date: '', end_date: '', duration_months: 0, description: '' },
  certifications: { name: '', issuer: '', year: '' }, projects: { title: '', description: '', technologies: '' } };
const num = (v) => (v === '' || v == null ? null : Number(v));

function SectionTitle({ icon: Icon, children, grad }) {
  return <h3 className="mb-3 flex items-center gap-2 text-base font-extrabold"><span className="icon-chip !h-8 !w-8 !rounded-xl" style={{ background: grad }}><Icon size={15} /></span>{children}</h3>;
}

function View({ p }) {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-muted">
        {p.email && <span className="flex items-center gap-1.5"><Mail size={14} />{p.email}</span>}
        {p.phone && <span className="flex items-center gap-1.5"><Phone size={14} />{p.phone}</span>}
        {p.location && <span className="flex items-center gap-1.5"><MapPin size={14} />{p.location}</span>}
        <Chip color="violet">{p.total_experience_years} yrs experience</Chip>
      </div>
      {p.summary && <p className="neu-inset p-4 text-sm">{p.summary}</p>}
      <div><SectionTitle icon={Sparkles} grad="linear-gradient(135deg,#2f6bff,#7a3cff)">Skills</SectionTitle>
        <div className="flex flex-wrap gap-2">{p.skills.length ? p.skills.map((s) => <Chip key={s.id ?? s.skill_name} color={s.skill_type === 'technical' ? 'blue' : 'orange'} title={`Evidence ${Math.round(s.evidence_weight * 100)}%`}>{s.skill_name}</Chip>) : <span className="text-sm text-muted">No skills detected. Use Edit to add them.</span>}</div></div>
      <div><SectionTitle icon={GraduationCap} grad="linear-gradient(135deg,#00c4a7,#2f6bff)">Education</SectionTitle>
        {p.education.length ? p.education.map((e, i) => <div key={i} className="neu-flat mb-3 p-4 text-sm"><b>{e.degree}{e.field_of_study && ` - ${e.field_of_study}`}</b><div className="text-muted">{[e.institution, [e.start_year, e.end_year].filter(Boolean).join(' - '), e.grade].filter(Boolean).join(' · ')}</div></div>) : <span className="text-sm text-muted">No education detected.</span>}</div>
      <div><SectionTitle icon={Briefcase} grad="linear-gradient(135deg,#ff3d95,#ff8a1f)">Experience</SectionTitle>
        {p.experience.length ? p.experience.map((e, i) => <div key={i} className="neu-flat mb-3 p-4 text-sm"><b>{e.title}</b>{e.company && <span> · {e.company}</span>}<div className="text-muted">{e.start_date} - {e.end_date} {e.duration_months ? `(${e.duration_months} months)` : ''}</div>{e.description && <p className="mt-1 text-muted">{e.description}</p>}</div>) : <span className="text-sm text-muted">No work experience detected.</span>}</div>
      <div className="grid gap-6 md:grid-cols-2">
        <div><SectionTitle icon={Award} grad="linear-gradient(135deg,#ffc226,#ff8a1f)">Certifications</SectionTitle>
          {p.certifications.length ? p.certifications.map((c, i) => <div key={i} className="mb-2 text-sm"><b>{c.name}</b> <span className="text-muted">{[c.issuer, c.year].filter(Boolean).join(' · ')}</span></div>) : <span className="text-sm text-muted">None detected.</span>}</div>
        <div><SectionTitle icon={FolderGit2} grad="linear-gradient(135deg,#7a3cff,#ff3d95)">Projects</SectionTitle>
          {p.projects.length ? p.projects.map((x, i) => <div key={i} className="mb-3 text-sm"><b>{x.title}</b><div className="text-muted">{x.description}</div>{x.technologies && <div className="mt-1 text-xs font-semibold text-bright-blue">{x.technologies}</div>}</div>) : <span className="text-sm text-muted">None detected.</span>}</div>
      </div>
    </div>
  );
}

function ListEditor({ title, icon, grad, items, onChange, kind, children }) {
  return (
    <div>
      <SectionTitle icon={icon} grad={grad}>{title}</SectionTitle>
      <div className="space-y-4">
        {items.map((it, i) => (
          <div key={i} className="neu-flat relative p-4 pr-12">
            <button type="button" aria-label={`Remove ${title} entry`} className="btn btn-sm absolute right-2 top-2 !p-2" onClick={() => onChange(items.filter((_, j) => j !== i))}><Trash2 size={14} /></button>
            <div className="grid gap-3 sm:grid-cols-2">{children(it, (k, v) => onChange(items.map((x, j) => (j === i ? { ...x, [k]: v } : x))))}</div>
          </div>))}
        <Btn size="sm" icon={Plus} type="button" onClick={() => onChange([...items, { ...blank[kind] }])}>Add {title.toLowerCase().replace(/s$/, '')}</Btn>
      </div>
    </div>
  );
}

function Editor({ profile, onSave, onCancel, saving, error }) {
  const [d, setD] = useState(() => structuredClone(profile));
  const [skill, setSkill] = useState('');
  const set = (k) => (e) => setD({ ...d, [k]: e.target.value });
  const addSkill = () => { const s = skill.trim(); if (s && !d.skills.some((x) => x.skill_name.toLowerCase() === s.toLowerCase())) setD({ ...d, skills: [...d.skills, { skill_name: s, skill_type: 'technical' }] }); setSkill(''); };
  const I = (v, on, ph, type = 'text') => <input className="field" type={type} value={v ?? ''} onChange={(e) => on(e.target.value)} placeholder={ph} />;
  function submit(e) {
    e.preventDefault();
    onSave({
      full_name: d.full_name, email: d.email, phone: d.phone, location: d.location, summary: d.summary || '',
      skills: d.skills.map((s) => ({ skill_name: s.skill_name, skill_type: s.skill_type })),
      education: d.education.filter((x) => x.degree.trim()).map((x) => ({ ...x, start_year: num(x.start_year), end_year: num(x.end_year), level: Number(x.level), id: undefined })),
      experience: d.experience.filter((x) => x.title.trim()).map((x) => ({ ...x, duration_months: Number(x.duration_months) || 0, id: undefined })),
      certifications: d.certifications.filter((x) => x.name.trim()).map((x) => ({ ...x, year: String(x.year || ''), id: undefined })),
      projects: d.projects.filter((x) => x.title.trim()).map((x) => ({ ...x, id: undefined })),
    });
  }
  return (
    <form onSubmit={submit} className="space-y-7">
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Full name"><input className="field" value={d.full_name} onChange={set('full_name')} /></Field>
        <Field label="Email"><input className="field" type="email" value={d.email} onChange={set('email')} /></Field>
        <Field label="Phone"><input className="field" value={d.phone} onChange={set('phone')} /></Field>
        <Field label="Location"><input className="field" value={d.location} onChange={set('location')} /></Field>
        <Field label="Professional summary" className="sm:col-span-2"><textarea className="field" rows={3} value={d.summary || ''} onChange={set('summary')} /></Field>
      </div>
      <div><SectionTitle icon={Sparkles} grad="linear-gradient(135deg,#2f6bff,#7a3cff)">Skills</SectionTitle>
        <div className="mb-3 flex flex-wrap gap-2">{d.skills.map((s) => <span key={s.skill_name} className="chip text-bright-blue">{s.skill_name}<button type="button" aria-label={`Remove ${s.skill_name}`} onClick={() => setD({ ...d, skills: d.skills.filter((x) => x !== s) })}><X size={13} /></button></span>)}</div>
        <div className="flex gap-3"><input className="field" value={skill} onChange={(e) => setSkill(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())} placeholder="Type a skill and press Enter" /><Btn type="button" icon={Plus} onClick={addSkill}>Add</Btn></div></div>
      <ListEditor title="Education" icon={GraduationCap} grad="linear-gradient(135deg,#00c4a7,#2f6bff)" items={d.education} kind="education" onChange={(v) => setD({ ...d, education: v })}>
        {(it, s) => <>
          <Field label="Degree *">{I(it.degree, (v) => s('degree', v), 'B.E.')}</Field><Field label="Field of study">{I(it.field_of_study, (v) => s('field_of_study', v), 'Computer Science')}</Field>
          <Field label="Institution" className="sm:col-span-2">{I(it.institution, (v) => s('institution', v), 'University / College')}</Field>
          <Field label="Start year">{I(it.start_year, (v) => s('start_year', v), '2018', 'number')}</Field><Field label="End year">{I(it.end_year, (v) => s('end_year', v), '2022', 'number')}</Field>
          <Field label="Grade">{I(it.grade, (v) => s('grade', v), 'CGPA 8.4')}</Field>
          <Field label="Level"><select className="field" value={it.level} onChange={(e) => s('level', e.target.value)}>{EDU_LEVELS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></Field></>}
      </ListEditor>
      <ListEditor title="Experience" icon={Briefcase} grad="linear-gradient(135deg,#ff3d95,#ff8a1f)" items={d.experience} kind="experience" onChange={(v) => setD({ ...d, experience: v })}>
        {(it, s) => <>
          <Field label="Job title *">{I(it.title, (v) => s('title', v), 'Software Engineer')}</Field><Field label="Company">{I(it.company, (v) => s('company', v), 'Company')}</Field>
          <Field label="Start (e.g. Jul 2022)">{I(it.start_date, (v) => s('start_date', v), 'Jul 2022')}</Field><Field label="End (or Present)">{I(it.end_date, (v) => s('end_date', v), 'Present')}</Field>
          <Field label="Duration (months)">{I(it.duration_months, (v) => s('duration_months', v), '12', 'number')}</Field>
          <Field label="Description" className="sm:col-span-2"><textarea className="field" rows={2} value={it.description || ''} onChange={(e) => s('description', e.target.value)} /></Field></>}
      </ListEditor>
      <ListEditor title="Certifications" icon={Award} grad="linear-gradient(135deg,#ffc226,#ff8a1f)" items={d.certifications} kind="certifications" onChange={(v) => setD({ ...d, certifications: v })}>
        {(it, s) => <><Field label="Name *" className="sm:col-span-2">{I(it.name, (v) => s('name', v), 'AWS Certified Cloud Practitioner')}</Field><Field label="Issuer">{I(it.issuer, (v) => s('issuer', v), 'Amazon')}</Field><Field label="Year">{I(it.year, (v) => s('year', v), '2023')}</Field></>}
      </ListEditor>
      <ListEditor title="Projects" icon={FolderGit2} grad="linear-gradient(135deg,#7a3cff,#ff3d95)" items={d.projects} kind="projects" onChange={(v) => setD({ ...d, projects: v })}>
        {(it, s) => <><Field label="Title *" className="sm:col-span-2">{I(it.title, (v) => s('title', v), 'Project name')}</Field><Field label="Technologies" className="sm:col-span-2">{I(it.technologies, (v) => s('technologies', v), 'Python, FastAPI')}</Field>
          <Field label="Description" className="sm:col-span-2"><textarea className="field" rows={2} value={it.description || ''} onChange={(e) => s('description', e.target.value)} /></Field></>}
      </ListEditor>
      <ErrorBox error={error} />
      <div className="flex flex-wrap gap-3"><Btn variant="primary" icon={Save} loading={saving} type="submit">Save changes</Btn>{onCancel && <Btn type="button" onClick={onCancel}>Cancel</Btn>}</div>
    </form>
  );
}

/** Read-only structured profile with an Edit toggle. onSave(payload) must return a promise. */
export default function ProfilePanel({ profile, onSave, startEditing = false, title = 'Extracted profile' }) {
  const [editing, setEditing] = useState(startEditing);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  async function save(payload) {
    setSaving(true); setError('');
    try { await onSave(payload); setEditing(false); } catch (e) { setError(errMsg(e)); } finally { setSaving(false); }
  }
  return (
    <Card>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div><h2 className="text-xl font-extrabold">{profile.full_name || title}</h2><p className="text-xs text-muted">{profile.is_edited ? 'Edited by you' : 'Detected automatically - please verify'}</p></div>
        {!editing && <Btn icon={Pencil} onClick={() => setEditing(true)}>Edit profile</Btn>}
      </div>
      {editing ? <Editor key={profile.id + String(editing)} profile={profile} onSave={save} onCancel={() => setEditing(false)} saving={saving} error={error} /> : <View p={profile} />}
    </Card>
  );
}
