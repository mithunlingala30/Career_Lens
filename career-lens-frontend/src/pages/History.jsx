import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Download, Eye } from 'lucide-react';
import { Evaluation, Reports, errMsg } from '../services/api';
import { Btn, Card, Chip, Empty, ErrorBox, PageHeader, Spinner, fmtDate } from '../components/ui';
import useFetch from '../hooks/useFetch';

const TYPES = { upload: ['blue', 'Upload'], matching: ['violet', 'Job matching'], evaluation: ['green', 'Evaluation'], recommendation: ['orange', 'Recommendation'] };
function Summary({ h }) {
  const s = h.scores || {};
  if (h.event_type === 'upload') return <span className="text-muted">{s.file_type?.toUpperCase()} · {s.size_kb} KB</span>;
  if (h.event_type === 'matching') return <span>Resume <b>{s.resume_score}</b> · top <b>{s.top_job}</b> {s.top_compatibility}% · {s.jobs_above_60} jobs ≥ 60%</span>;
  if (h.event_type === 'evaluation') return <span>Resume <b>{s.resume_score}</b> · {s.job_title} <b>{s.compatibility}%</b> · {s.matched} matched / {s.missing} missing</span>;
  return <span>{s.top_category}: suitability <b>{s.suitability}%</b>, readiness <b>{s.readiness}%</b></span>;
}

export default function HistoryPage() {
  const nav = useNavigate();
  const { data, loading, error, reload } = useFetch(Evaluation.history, []);
  const [type, setType] = useState(''); const [err, setErr] = useState('');
  if (loading) return <Spinner label="Loading history…" />;
  if (error) return <ErrorBox error={error} onRetry={reload} />;
  const rows = data.filter((h) => !type || h.event_type === type);
  return (
    <div><PageHeader title="Evaluation history" subtitle="Every upload, match, evaluation and recommendation - stored permanently">
      <select aria-label="Filter by type" className="field !w-auto" value={type} onChange={(e) => setType(e.target.value)}><option value="">All activity</option>{Object.entries(TYPES).map(([k, [, l]]) => <option key={k} value={k}>{l}</option>)}</select></PageHeader>
      <ErrorBox error={err} />
      {!rows.length ? <Empty title="No history yet" text="Your activity appears here once you upload and evaluate a resume." action="Upload resume" to="/app/upload" /> :
        <Card className="overflow-x-auto !p-2"><table className="table-neu w-full min-w-[720px]"><thead><tr><th>Date</th><th>Type</th><th>Resume</th><th>Result</th><th className="text-right">Report</th></tr></thead>
          <tbody>{rows.map((h) => (
            <tr key={h.id}><td className="whitespace-nowrap text-muted">{fmtDate(h.created_at)}</td><td><Chip color={TYPES[h.event_type][0]}>{TYPES[h.event_type][1]}</Chip></td><td className="max-w-[180px] truncate">{h.resume_name}</td><td><Summary h={h} /></td>
              <td><div className="flex justify-end gap-2">
                {h.resume_id && h.event_type !== 'upload' && <Btn size="sm" icon={Eye} onClick={() => nav(h.event_type === 'recommendation' ? '/app/careers' : h.job_id ? `/app/evaluation?job=${h.job_id}` : '/app/jobs')}>View</Btn>}
                {h.evaluation_id && <Btn size="sm" variant="primary" icon={Download} onClick={() => Reports.pdf(h.evaluation_id).catch((e) => setErr(errMsg(e)))}>PDF</Btn>}</div></td></tr>))}</tbody></table></Card>}
    </div>
  );
}
