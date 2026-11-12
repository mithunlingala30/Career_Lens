import { useResume } from '../context/ResumeContext';
import { Empty, Spinner } from './ui';

/** Renders children only when the candidate has an analysed resume selected. */
export default function ResumeGate({ children, needAnalysed = true }) {
  const { active, ready } = useResume();
  if (!ready) return <Spinner label="Loading your resumes…" />;
  if (!active) return <Empty title="No resume yet" text="Upload your resume to unlock evaluation, job matching and career recommendations." action="Upload a resume" to="/app/upload" />;
  if (needAnalysed && active.status !== 'extracted') return <Empty title="Resume not analysed" text="Open the upload page and run the analysis for this resume first." action="Go to upload" to="/app/upload" />;
  return children(active);
}
