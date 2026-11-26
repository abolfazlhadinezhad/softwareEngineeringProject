import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../features/auth/AuthProvider';
import { Alert, Field, Loading, ErrorState } from '../components/ui';

export default function LoginPage() {
  const auth = useAuth();
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  if (auth.isLoading) return <Loading />;
  if (auth.error) return <ErrorState error={auth.error} retry={auth.retry} />;
  if (auth.user) return <Navigate to="/tickets" replace />;
  async function submit(event) { event.preventDefault(); setError(''); setBusy(true); try { await auth.signIn(form); } catch (e) { setError(e.message); setBusy(false); } }
  return <main className="login-layout"><section className="login-story"><div className="brand"><span className="brand-mark">U</span><span>University<span className="brand-sub">SUPPORT DESK</span></span></div><div><div className="eyebrow">A BETTER WAY TO GET HELP</div><h1>Your questions.<br />A clear path forward.</h1><p>Connect with university support, keep every conversation together, and follow your request from start to resolution.</p><div className="story-rule" /><p className="story-note">ONE WORKSPACE. EVERY STEP ACCOUNTED FOR.</p></div><span>Built for students. Supported by people.</span></section><section className="login-form-region"><form className="login-form" onSubmit={submit}><div className="eyebrow">YOUR SUPPORT WORKSPACE</div><h2>Welcome back.</h2><p>Sign in with your university support account.</p><Alert>{error}</Alert><Field label="Username" name="username"><input id="username" name="username" autoComplete="username" required maxLength={150} value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} /></Field><Field label="Password" name="password"><input id="password" name="password" type="password" autoComplete="current-password" required maxLength={1024} value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} /></Field><button className="full" disabled={busy}>{busy ? 'Signing in…' : 'Sign in →'}</button><p className="login-help">Need an account? Contact your university administrator. Accounts are provided by the university.</p></form></section></main>;
}
