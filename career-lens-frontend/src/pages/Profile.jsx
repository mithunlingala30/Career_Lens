import { Mail, ShieldCheck } from 'lucide-react';
import { Analysis } from '../services/api';
import { Card, ErrorBox, PageHeader, Spinner, Empty } from '../components/ui';
import ProfilePanel from '../components/ProfilePanel';
import ResumeGate from '../components/ResumeGate';
import { useAuth } from '../context/AuthContext';
import useFetch from '../hooks/useFetch';

function Body({ resume }) {
  const { user } = useAuth();
  const { data, loading, error, reload } = useFetch(() => Analysis.get(resume.id), [resume.id]);
  return (
    <div className="grid gap-6 xl:grid-cols-4">
      <Card className="h-fit text-center"><div className="icon-chip mx-auto !h-20 !w-20 !rounded-full text-3xl font-extrabold" style={{ background: 'linear-gradient(135deg,#7a3cff,#ff3d95)' }}>{user.full_name[0]}</div>
        <h2 className="mt-4 text-lg font-extrabold">{user.full_name}</h2><p className="mt-1 flex items-center justify-center gap-1 text-sm text-muted"><Mail size={14} />{user.email}</p>
        <p className="mt-1 flex items-center justify-center gap-1 text-xs font-bold text-bright-teal"><ShieldCheck size={14} />Candidate account</p>
        <p className="mt-4 text-xs text-muted">Profile data below belongs to <b>{resume.original_filename}</b>. Saving changes re-calculates your scores.</p></Card>
      <div className="xl:col-span-3">{loading ? <Spinner /> : error ? <ErrorBox error={error} onRetry={reload} /> : <ProfilePanel profile={data} startEditing onSave={async (p) => { await Analysis.update(resume.id, p); await reload(); }} title="Your profile" />}</div>
    </div>
  );
}
export default function Profile() {
  return (<div><PageHeader title="My profile" subtitle="Personal information, education, skills, experience, certifications and projects" /><ResumeGate>{(r) => <Body resume={r} key={r.id} />}</ResumeGate></div>);
}
