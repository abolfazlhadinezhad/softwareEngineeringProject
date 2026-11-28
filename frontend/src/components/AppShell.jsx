import { useState } from 'react';
import { Link, NavLink, Outlet } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { useAuth } from '../features/auth/AuthProvider';
import { Alert, label } from './ui';

const management = [
  ['departments', 'واحدهای سازمانی', 'department.manage'],
  ['categories', 'دسته‌بندی‌ها', 'department.manage'],
  ['forms', 'فرم‌ساز', 'department.manage'],
  ['memberships', 'عضویت کارکنان', 'employee.manage'],
  ['roles', 'نقش‌ها و مجوزها', 'role.manage'],
  ['role-assignments', 'تخصیص نقش', 'role.manage'],
  ['calendars', 'تقویم کاری', 'settings.manage'],
  ['holidays', 'تعطیلات', 'settings.manage'],
  ['sla-policies', 'سیاست‌های SLA', 'settings.manage'],
  ['articles', 'مقالات راهنما', 'knowledge_base.publish'],
  ['faqs', 'پرسش‌های متداول', 'knowledge_base.publish'],
  ['announcements', 'اطلاعیه‌ها', 'knowledge_base.publish'],
];
export default function AppShell() {
  const { user, signOut } = useAuth();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const notifications = useQuery({
    queryKey: ['notifications'],
    queryFn: () => api('/notifications/'),
    refetchInterval: 15000,
  });
  const can = (permission) => user.capabilities?.includes(permission);
  async function logout() {
    setBusy(true);
    try {
      await signOut();
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  }
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        رفتن به محتوا
      </a>
      <aside className="sidebar">
        <Link className="brand" to="/dashboard">
          <span className="brand-mark">ن</span>
          <span>
            نوشیروانی بابل<small className="brand-sub">سامانه پشتیبانی دانشجویان</small>
          </span>
        </Link>
        <div className="sidebar-label">
          {user.role === 'student'
            ? 'پرتال دانشجو'
            : user.role === 'admin'
              ? 'مدیریت سامانه'
              : 'میز خدمت'}
        </div>
        <nav aria-label="راهبری پرتال">
          <NavLink to="/dashboard">
            ◈ <span>پیشخوان</span>
          </NavLink>
          <NavLink end to="/tickets">
            ▤ <span>{user.role === 'student' ? 'درخواست‌های من' : 'صف رسیدگی'}</span>
          </NavLink>
          {can('ticket.create') && (
            <NavLink to="/tickets/new">
              ＋ <span>درخواست جدید</span>
            </NavLink>
          )}
          <NavLink to="/notifications">
            ◌{' '}
            <span>
              اعلان‌ها {notifications.data?.unread ? '(' + notifications.data.unread + ')' : ''}
            </span>
          </NavLink>
          <NavLink to="/profile">
            ⚙ <span>حساب و امنیت</span>
          </NavLink>
          {management
            .filter(([, , permission]) => can(permission))
            .map(([path, title]) => (
              <NavLink key={path} to={'/manage/' + path}>
                <span>{title}</span>
              </NavLink>
            ))}
          {can('student.manage') && <NavLink to="/student-import">ورود گروهی دانشجویان</NavLink>}
          {can('audit.view') && <NavLink to="/audit">سوابق ممیزی</NavLink>}
          {can('settings.manage') && (
            <>
              <NavLink to="/system/health">سلامت سامانه</NavLink>
              <NavLink to="/system/settings">تنظیمات سامانه</NavLink>
            </>
          )}
          {can('ticket.export') && <a href="/api/v1/reports/tickets.csv">خروجی عملیاتی CSV</a>}
          <Link to="/knowledge">مرکز راهنما ↗</Link>
        </nav>
        <div className="sidebar-bottom">
          <div>
            <strong>{user.first_name || user.username}</strong>
            <small>{label(user.role)}</small>
          </div>
          <button className="signout" onClick={logout} disabled={busy}>
            {busy ? 'در حال خروج…' : 'خروج'}
          </button>
        </div>
      </aside>
      <main id="main" className="workspace">
        <div className="topbar">
          <span>دانشگاه صنعتی نوشیروانی بابل / {label(user.role)}</span>
          <Link to="/">وب‌سایت عمومی ↗</Link>
        </div>
        <Alert>{error}</Alert>
        <Outlet />
      </main>
    </div>
  );
}
