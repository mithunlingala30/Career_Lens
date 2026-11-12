import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import AppLayout from './layouts/AppLayout';
import { Spinner } from './components/ui';
import Landing from './pages/Landing';
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
import Dashboard from './pages/Dashboard';
import ResumeUpload from './pages/ResumeUpload';
import Evaluation from './pages/Evaluation';
import Jobs from './pages/Jobs';
import Careers from './pages/Careers';
import SkillGaps from './pages/SkillGaps';
import HistoryPage from './pages/History';
import Profile from './pages/Profile';
import AdminDashboard from './pages/AdminDashboard';

function Protected({ role, children }) {
  const { user, loading } = useAuth();
  const loc = useLocation();
  if (loading) return <div className="min-h-screen"><Spinner label="Checking your session…" /></div>;
  if (!user) return <Navigate to="/login" state={{ from: loc.pathname }} replace />;
  if (user.role !== role) return <Navigate to={user.role === 'admin' ? '/admin' : '/app/dashboard'} replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login mode="login" />} />
      <Route path="/register" element={<Login mode="register" />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/app" element={<Protected role="candidate"><AppLayout /></Protected>}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="upload" element={<ResumeUpload />} />
        <Route path="evaluation" element={<Evaluation />} />
        <Route path="jobs" element={<Jobs />} />
        <Route path="careers" element={<Careers />} />
        <Route path="skill-gaps" element={<SkillGaps />} />
        <Route path="history" element={<HistoryPage />} />
        <Route path="profile" element={<Profile />} />
      </Route>
      <Route path="/admin" element={<Protected role="admin"><AppLayout /></Protected>}>
        <Route index element={<AdminDashboard />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
