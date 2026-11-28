import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../services/api';
import { Alert, ErrorState, Field, Loading, PageHeader } from '../components/ui';

export function SystemHealthPage() {
  const query = useQuery({
    queryKey: ['health'],
    queryFn: () => api('/manage/health/'),
    refetchInterval: 15000,
  });
  if (query.isPending) return <Loading />;
  if (query.error) return <ErrorState error={query.error} retry={query.refetch} />;
  return (
    <>
      <PageHeader title="سلامت سرویس‌ها" />
      <section className="panel panel-pad">
        {[
          ['database', 'پایگاه داده MySQL'],
          ['redis', 'حافظه و صف Redis'],
          ['worker', 'پایش پس‌زمینه Celery'],
        ].map(([key, title]) => (
          <div className="report-row" key={key}>
            <strong>{title}</strong>
            <span role="status">{query.data[key] ? '✓ در دسترس' : '⚠ نیازمند بررسی'}</span>
          </div>
        ))}
        <p className="notice">وضعیت پردازشگر بر اساس آخرین اجرای پایش دوره‌ای نمایش داده می‌شود.</p>
      </section>
    </>
  );
}

export function SystemSettingsPage() {
  const query = useQuery({ queryKey: ['settings'], queryFn: () => api('/manage/settings/') });
  const [changes, setChanges] = useState({});
  const mutation = useMutation({
    mutationFn: () => api('/manage/settings/', { method: 'PATCH', body: changes }),
    onSuccess: () => query.refetch(),
  });
  if (query.isPending) return <Loading />;
  if (query.error) return <ErrorState error={query.error} retry={query.refetch} />;
  return (
    <div className="form-wrap">
      <PageHeader title="تنظیمات سامانه" />
      <form
        className="panel panel-pad"
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate();
        }}
      >
        <Alert>{mutation.error?.message}</Alert>
        {[
          ['university_name', 'نام دانشگاه'],
          ['site_title', 'عنوان سامانه'],
          ['contact_email', 'ایمیل پشتیبانی'],
          ['support_hours', 'ساعات پاسخگویی'],
          ['auto_close_days', 'مهلت تأیید نتیجه (روز)'],
          ['reopen_days', 'مهلت بازگشایی (روز)'],
        ].map(([key, title]) => (
          <Field key={key} label={title} name={key}>
            <input
              id={key}
              required={key !== 'contact_email'}
              type={key.endsWith('_days') ? 'number' : key === 'contact_email' ? 'email' : 'text'}
              value={changes[key] ?? query.data[key]}
              onChange={(e) => setChanges({ ...changes, [key]: e.target.value })}
            />
          </Field>
        ))}
        <button disabled={mutation.isPending}>ذخیره تنظیمات</button>
        {mutation.isSuccess && <p role="status">تنظیمات ذخیره شد.</p>}
      </form>
    </div>
  );
}
