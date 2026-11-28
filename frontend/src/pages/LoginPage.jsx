import { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../features/auth/AuthProvider';
import { Alert, Field, Loading, ErrorState } from '../components/ui';

export default function LoginPage({ portal = 'student' }) {
  const auth = useAuth();
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  if (auth.isLoading) return <Loading />;
  if (auth.error) return <ErrorState error={auth.error} retry={auth.retry} />;
  if (auth.user) return <Navigate to="/dashboard" replace />;
  async function submit(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      await auth.signIn({ ...form, portal });
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  }
  const title =
    portal === 'student'
      ? 'ورود دانشجویان'
      : portal === 'staff'
        ? 'ورود کارکنان'
        : 'ورود مدیران سامانه';
  return (
    <main className="login-layout" dir="rtl">
      <section className="login-story">
        <Link className="brand" to="/">
          <span className="brand-mark">ن</span>
          <span>
            دانشگاه صنعتی نوشیروانی بابل
            <small className="brand-sub">سامانه پاسخگویی و پشتیبانی</small>
          </span>
        </Link>
        <div>
          <div className="eyebrow">هر درخواست، یک مسیر روشن</div>
          <h1>
            پاسخگویی منظم.
            <br />
            پیگیری تا نتیجه.
          </h1>
          <p>گفت‌وگو با واحد مسئول، مشاهده روند رسیدگی و دریافت پاسخ در یک محیط امن.</p>
        </div>
        <Link to="/">بازگشت به مرکز راهنمای عمومی ←</Link>
      </section>
      <section className="login-form-region">
        <form className="login-form" onSubmit={submit}>
          <div className="eyebrow">حساب دانشگاهی</div>
          <h2>{title}</h2>
          <p>با حسابی که دانشگاه در اختیار شما قرار داده است وارد شوید.</p>
          <Alert>{error}</Alert>
          <Field label={portal === 'student' ? 'شماره دانشجویی' : 'نام کاربری'} name="username">
            <input
              id="username"
              dir="ltr"
              autoComplete="username"
              required
              maxLength={150}
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
            />
          </Field>
          <Field label="رمز عبور" name="password">
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              maxLength={1024}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </Field>
          <button className="full" disabled={busy}>
            {busy ? 'در حال ورود…' : 'ورود به سامانه ←'}
          </button>
          <p className="login-help">
            حساب فعال نشده است؟ <Link to="/activate">فعال‌سازی حساب</Link>
            <br />
            برای دریافت حساب یا بازیابی دسترسی با مسئول مجاز دانشگاه تماس بگیرید.
          </p>
          <div className="hero-links">
            <Link to="/login">دانشجو</Link>
            <Link to="/staff/login">کارکنان</Link>
            <Link to="/control/login">مدیر سامانه</Link>
          </div>
        </form>
      </section>
    </main>
  );
}
