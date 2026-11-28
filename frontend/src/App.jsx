import { Navigate, Outlet, Route, Routes, Link } from 'react-router-dom';
import { useAuth } from './features/auth/AuthProvider';
import AppShell from './components/AppShell';
import { Loading, ErrorState } from './components/ui';
import LoginPage from './pages/LoginPage';
import TicketQueuePage from './pages/TicketQueuePage';
import TicketWizard from './pages/TicketWizard';
import TicketDetailPage from './pages/TicketDetailPage';
import PortalDashboard from './pages/PortalDashboard';
import { SystemHealthPage, SystemSettingsPage } from './pages/SystemPages';
import AdminResourcePage, { AuditPage } from './pages/AdminResourcePage';
import {
  ActivationPage,
  NotificationsPage,
  ProfilePage,
  StudentImportPage,
} from './pages/AccountPages';
import {
  PublicLayout,
  HomePage,
  KnowledgePage,
  ArticlePage,
  FAQPage,
  DepartmentsPage,
  AnnouncementsPage,
  InformationPage,
} from './pages/PublicPages';

function Protected() {
  const auth = useAuth();
  if (auth.isLoading) return <Loading />;
  if (auth.error) return <ErrorState error={auth.error} retry={auth.retry} />;
  return auth.user ? <Outlet /> : <Navigate to="/login" replace />;
}
function Permit({ permission }) {
  const { user } = useAuth();
  return user.capabilities?.includes(permission) ? (
    <Outlet />
  ) : (
    <main className="state">
      <h1>دسترسی مجاز نیست</h1>
      <Link to="/dashboard">بازگشت به پیشخوان</Link>
    </main>
  );
}
export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/knowledge/:id" element={<ArticlePage />} />
        <Route path="/faq" element={<FAQPage />} />
        <Route path="/departments" element={<DepartmentsPage />} />
        <Route path="/departments/:id" element={<DepartmentsPage />} />
        <Route path="/announcements" element={<AnnouncementsPage />} />
        <Route path="/announcements/:id" element={<AnnouncementsPage />} />
        {['about', 'privacy', 'accessibility'].map((kind) => (
          <Route key={kind} path={'/' + kind} element={<InformationPage kind={kind} />} />
        ))}
        <Route path="/activate" element={<ActivationPage />} />
      </Route>
      <Route path="/login" element={<LoginPage portal="student" />} />
      <Route path="/staff/login" element={<LoginPage portal="staff" />} />
      <Route path="/control/login" element={<LoginPage portal="admin" />} />
      <Route element={<Protected />}>
        <Route element={<AppShell />}>
          <Route path="/dashboard" element={<PortalDashboard />} />
          <Route path="/tickets" element={<TicketQueuePage />} />
          <Route path="/tickets/:id" element={<TicketDetailPage />} />
          <Route element={<Permit permission="ticket.create" />}>
            <Route path="/tickets/new" element={<TicketWizard />} />
          </Route>
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route element={<Permit permission="settings.manage" />}>
            <Route path="/system/health" element={<SystemHealthPage />} />
            <Route path="/system/settings" element={<SystemSettingsPage />} />
          </Route>
          <Route element={<Permit permission="student.manage" />}>
            <Route path="/student-import" element={<StudentImportPage />} />
          </Route>
          <Route element={<Permit permission="audit.view" />}>
            <Route path="/audit" element={<AuditPage />} />
          </Route>
          <Route path="/manage/:resource" element={<AdminResourcePage />} />
        </Route>
      </Route>
      <Route
        path="*"
        element={
          <main className="state">
            <h1>صفحه پیدا نشد</h1>
            <Link to="/">بازگشت به خانه</Link>
          </main>
        }
      />
    </Routes>
  );
}
