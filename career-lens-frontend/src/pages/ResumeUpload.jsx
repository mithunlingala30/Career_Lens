import { useCallback, useEffect, useRef, useState } from 'react';
import { CheckCircle2, CircleDashed, FileText, Trash2, UploadCloud, Eye, RefreshCw, Loader2 } from 'lucide-react';
import { Analysis, Matching, Recs, Resumes, errMsg } from '../services/api';
import { Btn, Card, Chip, ErrorBox, Notice, PageHeader, ProgressBar, fmtDate } from '../components/ui';
import ProfilePanel from '../components/ProfilePanel';
import { useResume } from '../context/ResumeContext';
import useFetch from '../hooks/useFetch';

const STEPS = ['Uploading file', 'Extracting resume information', 'Matching against jobs', 'Building career recommendations'];

function Preview({ resume }) {
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [mode, setMode] = useState(resume.file_type === 'pdf' ? 'file' : 'text');
  useEffect(() => {
    let revoke = '';
    setUrl(''); setText('');
    if (resume.file_type === 'pdf') Resumes.fileBlob(resume.id).then((b) => { revoke = URL.createObjectURL(b); setUrl(revoke); }).catch(() => {});
    Resumes.get(resume.id).then((r) => setText(r.raw_text)).catch(() => {});
    return () => revoke && URL.revokeObjectURL(revoke);
  }, [resume.id, resume.file_type]);
  return (
    <Card>
      <div className="mb-3 flex items-center justify-between"><h2 className="text-lg font-extrabold">Resume preview</h2>
        {resume.file_type === 'pdf' && <div className="flex gap-2">{['file', 'text'].map((m) => <button key={m} className={`btn btn-sm ${mode === m ? 'btn-primary' : ''}`} onClick={() => setMode(m)}>{m === 'file' ? 'Original' : 'Extracted text'}</button>)}</div>}</div>
      {mode === 'file' && url ? <iframe title="Resume preview" src={url} className="neu-inset h-[520px] w-full" />
        : <pre className="neu-inset max-h-[520px] overflow-auto whitespace-pre-wrap p-4 text-xs leading-relaxed">{text || 'Loading text…'}</pre>}
    </Card>
  );
}

export default function ResumeUpload() {
  const { resumes, active, activeId, setActiveId, refresh } = useResume();
  const [drag, setDrag] = useState(false);
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState(-1);
  const [err, setErr] = useState('');
  const [info, setInfo] = useState('');
  const input = useRef();
  const [ver, setVer] = useState(0);
  const profile = useFetch(() => Analysis.get(activeId), [activeId, ver], !!active && active.status === 'extracted');

  const pipeline = useCallback(async (id) => {
    setStep(1); await Analysis.extract(id);
    setStep(2); await Matching.run(id);
    setStep(3); await Recs.run(id);
    setStep(4);
    await refresh(id); setVer((v) => v + 1);
  }, [refresh]);

  async function handle(file) {
    setErr(''); setInfo('');
    if (!file) return;
    if (!/\.(pdf|docx)$/i.test(file.name)) return setErr('Only PDF and DOCX files are supported.');
    if (file.size > 10 * 1024 * 1024) return setErr('File is larger than 10 MB.');
    try {
      setStep(0); setProgress(0);
      const r = await Resumes.upload(file, setProgress);
      await refresh(r.id);
      await pipeline(r.id);
      setInfo('Resume analysed. Review the extracted details below and correct anything that looks wrong.');
    } catch (e) { setErr(errMsg(e)); setStep(-1); }
  }

  async function reanalyse() {
    setErr(''); setInfo('');
    try { setStep(2); await Matching.run(activeId); setStep(3); await Recs.run(activeId); setStep(4); await refresh(activeId); setInfo('Scores and recommendations refreshed using your corrected profile.'); }
    catch (e) { setErr(errMsg(e)); setStep(-1); }
  }
  async function runExtract() {
    setErr('');
    try { await pipeline(activeId); } catch (e) { setErr(errMsg(e)); setStep(-1); }
  }
  async function remove(id) {
    if (!window.confirm('Delete this resume and its evaluations? Your history entries are kept.')) return;
    try { await Resumes.remove(id); await refresh(); } catch (e) { setErr(errMsg(e)); }
  }
  async function saveProfile(payload) {
    await Analysis.update(activeId, payload);
    await profile.reload();
    await reanalyse();
  }
  const busy = step >= 0 && step < 4;

  return (
    <div>
      <PageHeader title="Resume upload & analysis" subtitle="Upload a PDF or DOCX resume. We extract your details, score them and match you to jobs." />
      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <div role="button" tabIndex={0} aria-label="Upload resume" onClick={() => !busy && input.current.click()} onKeyDown={(e) => e.key === 'Enter' && input.current.click()}
            onDragOver={(e) => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)} onDrop={(e) => { e.preventDefault(); setDrag(false); handle(e.dataTransfer.files[0]); }}
            className="neu flex cursor-pointer flex-col items-center gap-4 px-6 py-14 text-center transition" style={drag ? { boxShadow: 'inset 8px 8px 16px #c3cbe0, inset -8px -8px 16px #fff', outline: '3px dashed #7a3cff' } : {}}>
            <div className="icon-chip !h-16 !w-16" style={{ background: 'linear-gradient(135deg,#2f6bff,#ff3d95)', boxShadow: '5px 8px 20px rgba(122,60,255,.4)' }}><UploadCloud size={30} /></div>
            <div><b className="text-lg">Drag & drop your resume here</b><p className="mt-1 text-sm text-muted">or click to browse · PDF or DOCX · up to 10 MB</p></div>
            <input ref={input} type="file" hidden accept=".pdf,.docx" onChange={(e) => { handle(e.target.files[0]); e.target.value = ''; }} />
          </div>
          {step >= 0 && (
            <Card className="mt-6">
              {step === 0 && <div className="mb-4"><div className="mb-1 flex justify-between text-xs font-bold text-muted"><span>Upload progress</span><span>{progress}%</span></div><ProgressBar value={progress} /></div>}
              <ol className="space-y-3">{STEPS.map((s, i) => (
                <li key={s} className="flex items-center gap-3 text-sm font-semibold" style={{ color: i < step ? '#009e87' : i === step ? '#7a3cff' : '#8d98bb' }}>
                  {i < step ? <CheckCircle2 size={18} /> : i === step ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <CircleDashed size={18} />}{s}</li>))}</ol>
            </Card>)}
          <div className="mt-6 space-y-3"><ErrorBox error={err} />{info && <Notice tone="green">{info}</Notice>}</div>
        </div>
        <Card className="lg:col-span-2">
          <h2 className="mb-4 text-lg font-extrabold">Your resumes</h2>
          {!resumes.length ? <p className="text-sm text-muted">Nothing uploaded yet.</p> : (
            <ul className="space-y-3">{resumes.map((r) => (
              <li key={r.id} className={`flex items-center gap-3 p-3 ${r.id === activeId ? 'neu-inset' : 'neu-flat'}`}>
                <FileText size={20} className="shrink-0 text-bright-violet" />
                <button className="min-w-0 flex-1 text-left" onClick={() => setActiveId(r.id)}><div className="truncate text-sm font-bold">{r.original_filename}</div><div className="text-xs text-muted">{fmtDate(r.created_at)}</div></button>
                {r.resume_score != null && <Chip color="green">{Math.round(r.resume_score)}</Chip>}
                <button aria-label={`Delete ${r.original_filename}`} className="btn btn-sm !p-2" onClick={() => remove(r.id)}><Trash2 size={14} /></button>
              </li>))}</ul>)}
        </Card>
      </div>
      {active && (
        <div className="mt-8 grid gap-6 xl:grid-cols-2">
          <Preview resume={active} />
          <div>
            {active.status !== 'extracted' ? <Card className="text-center"><p className="mb-4 text-sm text-muted">This resume has not been analysed yet.</p><Btn variant="primary" icon={Eye} loading={busy} onClick={runExtract}>Analyse now</Btn></Card>
              : profile.loading ? <Card><div className="py-10 text-center text-sm text-muted">Loading extracted data…</div></Card>
              : profile.error ? <ErrorBox error={profile.error} onRetry={profile.reload} />
              : profile.data && <><ProfilePanel profile={profile.data} onSave={saveProfile} />
                <div className="mt-4"><Btn icon={RefreshCw} loading={busy} onClick={runExtract} size="sm">Re-extract from original file</Btn></div></>}
          </div>
        </div>)}
    </div>
  );
}
