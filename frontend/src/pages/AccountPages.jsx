import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { Alert, EmptyState, ErrorState, Field, Loading, PageHeader, date } from '../components/ui';

export function ActivationPage() {
  const [form, setForm] = useState({ token: '', password: '' });
  const mutation = useMutation({
    mutationFn: () => api('/auth/activate/', { method: 'POST', body: form }),
    onSuccess: () => setForm({ token: '', password: '' }),
  });
  return (
    <main className="reading-page">
      <PageHeader title="فعال‌سازی حساب دانشگاهی" />
      <p>
        کد محرمانه فعال‌سازی را از مسیر مورد تأیید دانشگاه دریافت کنید. این کد یک‌بارمصرف است و ۲۴
        ساعت اعتبار دارد.
      </p>
      {mutation.isSuccess ? (
        <div role="status">
          حساب فعال شد. <Link to="/login">ورود به سامانه</Link>
        </div>
      ) : (
        <form
          className="panel panel-pad"
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate();
          }}
        >
          <Alert>{mutation.error?.message}</Alert>
          <Field label="کد فعال‌سازی" name="token">
            <input
              id="token"
              dir="ltr"
              autoComplete="off"
              required
              value={form.token}
              onChange={(e) => setForm({ ...form, token: e.target.value })}
            />
          </Field>
          <Field label="رمز عبور جدید" name="password">
            <input
              id="password"
              required
              type="password"
              minLength={10}
              autoComplete="new-password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </Field>
          <button disabled={mutation.isPending}>فعال‌سازی حساب</button>
        </form>
      )}
    </main>
  );
}

export function NotificationsPage() {
  const client = useQueryClient();
  const query = useQuery({
    queryKey: ['notifications'],
    queryFn: () => api('/notifications/'),
    refetchInterval: 15000,
  });
  const mutation = useMutation({
    mutationFn: (id) => api('/notifications/', { method: 'POST', body: id ? { id } : {} }),
    onSuccess: () => client.invalidateQueries({ queryKey: ['notifications'] }),
  });
  if (query.isPending) return <Loading />;
  if (query.error) return <ErrorState error={query.error} retry={query.refetch} />;
  return (
    <>
      <PageHeader
        title="اعلان‌های شما"
        action={
          <button disabled={mutation.isPending} onClick={() => mutation.mutate(null)}>
            علامت‌گذاری همه به‌عنوان خوانده‌شده
          </button>
        }
      />
      <Alert>{mutation.error?.message}</Alert>
      <div className="panel panel-pad">
        {query.data.results.length ? (
          query.data.results.map((n) => (
            <div className="ticket-row" key={n.id}>
              <div>
                {n.ticket_id ? (
                  <Link to={'/tickets/' + n.ticket_id}>{n.title}</Link>
                ) : (
                  <strong>{n.title}</strong>
                )}
                <small>{date(n.created_at)}</small>
              </div>
              {!n.is_read && (
                <button
                  className="secondary"
                  disabled={mutation.isPending}
                  onClick={() => mutation.mutate(n.id)}
                >
                  خواندم
                </button>
              )}
            </div>
          ))
        ) : (
          <EmptyState title="اعلانی وجود ندارد" />
        )}
      </div>
    </>
  );
}

export function ProfilePage() {
  const query = useQuery({ queryKey: ['profile'], queryFn: () => api('/profile/') });
  const [password, setPassword] = useState({ current_password: '', password: '' });
  const mutation = useMutation({
    mutationFn: () => api('/auth/password/', { method: 'POST', body: password }),
    onSuccess: () => setPassword({ current_password: '', password: '' }),
  });
  const preferences = useMutation({
    mutationFn: (enabled) =>
      api('/profile/', {
        method: 'PATCH',
        body: { notification_preferences: { in_app: enabled } },
      }),
    onSuccess: () => query.refetch(),
  });
  if (query.isPending) return <Loading />;
  if (query.error) return <ErrorState error={query.error} retry={query.refetch} />;
  const p = query.data;
  return (
    <>
      <PageHeader title="حساب و امنیت" />
      <div className="detail-grid">
        <section className="panel panel-pad">
          <h2>اطلاعات دانشگاهی</h2>
          <dl className="metadata">
            {[
              ['نام', p.first_name + ' ' + p.last_name],
              ['شناسه', p.username],
              ['ایمیل دانشگاهی', p.email],
              ['دانشکده', p.faculty],
              ['رشته', p.program],
              ['مقطع', p.degree],
              ['سال ورود', p.admission_year],
            ].map(([k, v]) => (
              <div key={k}>
                <dt>{k}</dt>
                <dd>{v || 'ثبت نشده'}</dd>
              </div>
            ))}
          </dl>
          <p className="notice">
            اصلاح اطلاعات هویتی و تحصیلی از طریق مسئول مجاز دانشگاه انجام می‌شود.
          </p>
          <h2>ترجیحات اعلان</h2>
          <Alert>{preferences.error?.message}</Alert>
          <label className="check-label">
            <input
              type="checkbox"
              checked={p.notification_preferences.in_app !== false}
              disabled={preferences.isPending}
              onChange={(e) => preferences.mutate(e.target.checked)}
            />{' '}
            دریافت اعلان‌های درون سامانه
          </label>
        </section>
        <form
          className="panel panel-pad"
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate();
          }}
        >
          <h2>تغییر رمز عبور</h2>
          <Alert>{mutation.error?.message}</Alert>
          {mutation.isSuccess && <p role="status">رمز عبور تغییر کرد؛ نشست‌های قبلی باطل شدند.</p>}
          <Field label="رمز فعلی" name="current-password">
            <input
              id="current-password"
              type="password"
              required
              autoComplete="current-password"
              value={password.current_password}
              onChange={(e) => setPassword({ ...password, current_password: e.target.value })}
            />
          </Field>
          <Field label="رمز جدید" name="new-password">
            <input
              id="new-password"
              type="password"
              minLength={10}
              required
              autoComplete="new-password"
              value={password.password}
              onChange={(e) => setPassword({ ...password, password: e.target.value })}
            />
          </Field>
          <button disabled={mutation.isPending}>ذخیره رمز جدید</button>
        </form>
      </div>
    </>
  );
}

export function StudentImportPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const mutation = useMutation({
    mutationFn: () => {
      const body = new FormData();
      body.append('file', file);
      return api('/manage/student-imports/', { method: 'POST', body });
    },
    onSuccess: setPreview,
  });
  const commit = useMutation({
    mutationFn: () =>
      api('/manage/student-imports/' + preview.id + '/commit/', { method: 'POST', body: {} }),
  });
  return (
    <>
      <PageHeader title="ورود گروهی دانشجویان" />
      <section className="panel panel-pad">
        <p>
          CSV با UTF-8؛ حداکثر ۱۰۰۰ ردیف. حساب‌ها تا دریافت کد فعال‌سازی و تعیین رمز غیرفعال
          می‌مانند.
        </p>
        <p>
          ستون‌های لازم: <code dir="ltr">student_number,first_name,last_name,email</code>
        </p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setPreview(null);
            commit.reset();
            mutation.mutate();
          }}
        >
          <Field label="فایل CSV" name="import-file">
            <input
              id="import-file"
              type="file"
              accept=".csv"
              required
              onChange={(e) => setFile(e.target.files[0])}
            />
          </Field>
          <button disabled={mutation.isPending}>اعتبارسنجی و پیش‌نمایش</button>
        </form>
        <Alert>{mutation.error?.message || commit.error?.message}</Alert>
        {preview && (
          <>
            <h2>نتیجه اعتبارسنجی: {preview.total} ردیف</h2>
            {preview.errors.map((e) => (
              <p role="alert" key={e.row}>
                ردیف {e.row}: {e.error}
              </p>
            ))}
            <div className="table-region">
              <table>
                <thead>
                  <tr>
                    <th>شماره دانشجویی</th>
                    <th>نام</th>
                    <th>ایمیل</th>
                  </tr>
                </thead>
                <tbody>
                  {preview.rows.map((r, i) => (
                    <tr key={i}>
                      <td>{r.student_number}</td>
                      <td>
                        {r.first_name} {r.last_name}
                      </td>
                      <td dir="ltr">{r.email}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="notice">
              حداکثر ۲۰ ردیف نخست نمایش داده می‌شود. تأیید، همه ردیف‌های معتبر را در یک تراکنش وارد
              می‌کند.
            </p>
            {commit.isSuccess ? (
              <p role="status">{commit.data.imported} حساب وارد شد.</p>
            ) : (
              <button
                disabled={!preview.can_commit || commit.isPending}
                onClick={() => commit.mutate()}
              >
                تأیید و ایجاد حساب‌ها
              </button>
            )}
          </>
        )}
      </section>
    </>
  );
}
