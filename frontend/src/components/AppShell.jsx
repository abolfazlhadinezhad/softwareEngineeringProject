import { useState } from 'react';
import { Link, NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../features/auth/AuthProvider';
import { Alert, label } from './ui';

export default function AppShell() {
  const { user, signOut } = useAuth();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function logout() { setBusy(true); try { await signOut(); } catch (e) { setError(e.message); setBusy(false); } }
  return <div className="app-shell"><a className="skip-link" href="#main">Skip to content</a><aside className="sidebar"><Link className="brand" to="/tickets"><span className="brand-mark" aria-hidden="true">U</span><span>University<span className="brand-sub">SUPPORT DESK</span></span></Link><div className="sidebar-label">WORKSPACE</div><nav aria-label="Main navigation"><NavLink end to="/tickets">▦ <span>Overview & tickets</span></NavLink>{user.role === 'student' && <NavLink to="/tickets/new">＋ <span>New ticket</span></NavLink>}{user.role === 'admin' && <a href="/admin/">↗ <span>Administration</span></a>}</nav><div className="sidebar-bottom"><div className="avatar">{user.username.slice(0, 1).toUpperCase()}</div><div><strong>{user.first_name || user.username}</strong><small>{label(user.role)}</small></div><button className="signout" onClick={logout} disabled={busy}>{busy ? 'Signing out…' : 'Sign out'}</button></div></aside><main id="main" className="workspace"><div className="topbar"><span>UNIVERSITY SERVICES / SUPPORT</span><span className="private-label">● Private workspace</span></div><Alert>{error}</Alert><Outlet /></main></div>;
}
