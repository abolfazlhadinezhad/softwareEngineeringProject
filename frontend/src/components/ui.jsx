import { Link } from 'react-router-dom';

const labels = {
  open: 'باز و در صف',
  in_progress: 'در حال بررسی',
  waiting_student: 'منتظر پاسخ دانشجو',
  resolved: 'حل‌شده',
  closed: 'بسته‌شده',
  low: 'کم',
  normal: 'عادی',
  high: 'زیاد',
  student: 'دانشجو',
  support: 'کارشناس',
  admin: 'مدیر سامانه',
  created: 'ثبت درخواست',
  replied: 'پاسخ جدید',
  claimed: 'تعیین مسئول',
  released: 'بازگشت به صف',
  status_changed: 'تغییر وضعیت',
  reopened: 'بازگشایی',
};
export const label = (value) => labels[value] || value || 'بدون مسئول';
export const date = (value) =>
  value
    ? new Date(value).toLocaleString('fa-IR', {
        dateStyle: 'medium',
        timeStyle: 'short',
        timeZone: 'Asia/Tehran',
      })
    : 'تعیین نشده';
export function Badge({ value }) {
  return <span className={'badge badge-' + value}>{label(value)}</span>;
}
export function Alert({ children }) {
  return children ? (
    <div role="alert" className="alert">
      {children}
    </div>
  ) : null;
}
export function Loading({ children = 'در حال بارگذاری…' }) {
  return (
    <div role="status" className="state">
      <span className="spinner" />
      {children}
    </div>
  );
}
export function ErrorState({ error, retry }) {
  return (
    <div className="panel state">
      <h2>بارگذاری صفحه انجام نشد</h2>
      <p role="alert">{error?.message || 'اتصال اینترنت را بررسی کنید.'}</p>
      {retry && <button onClick={() => retry()}>تلاش مجدد</button>}
    </div>
  );
}
export function EmptyState({ title, children }) {
  return (
    <div className="state">
      <div className="empty-icon" aria-hidden="true">
        ↗
      </div>
      <h2>{title}</h2>
      <p>{children}</p>
    </div>
  );
}
export function PageHeader({ eyebrow, title, children, action }) {
  return (
    <header className="page-header">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        {children && <div className="notice">{children}</div>}
      </div>
      {action}
    </header>
  );
}
export function Field({ label: text, name, error, children, hint }) {
  return (
    <div className="field">
      <label htmlFor={name}>{text}</label>
      {children}
      {hint && <small id={name + '-hint'}>{hint}</small>}
      {error && (
        <small className="field-error" id={name + '-error'}>
          {Array.isArray(error) ? error.join(' ') : error}
        </small>
      )}
    </div>
  );
}
export function Pagination({ data, page, onPage }) {
  return data && data.count > 20 ? (
    <nav className="pagination" aria-label="صفحه‌بندی">
      <button className="secondary" disabled={!data.previous} onClick={() => onPage(page - 1)}>
        قبلی
      </button>
      <span>
        صفحه {page} · {data.count} نتیجه
      </span>
      <button className="secondary" disabled={!data.next} onClick={() => onPage(page + 1)}>
        بعدی
      </button>
    </nav>
  ) : null;
}
export function BackLink() {
  return (
    <Link className="back-link" to="/tickets">
      همه درخواست‌ها ←
    </Link>
  );
}
