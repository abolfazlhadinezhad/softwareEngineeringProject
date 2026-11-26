import { Navigate, Outlet, Route, Routes, Link } from 'react-router-dom';
import { useAuth } from './features/auth/AuthProvider';
import AppShell from './components/AppShell';
import { Loading, ErrorState } from './components/ui';
import LoginPage from './pages/LoginPage';

function Protected() { const auth = useAuth(); if (auth.isLoading) return <Loading />; if (auth.error) return <ErrorState error={auth.error} retry={auth.retry} />; return auth.user ? <Outlet /> : <Navigate to="/login" replace />; }
export default function App() { return <Routes><Route path="/login" element={<LoginPage />} /><Route element={<Protected />}><Route element={<AppShell />}><Route path="/tickets" element={<section><h1>Support workspace</h1><p>Authenticated foundation ready. Ticket workflow implementation is in progress.</p></section>} /></Route></Route><Route path="/" element={<Navigate to="/tickets" replace />} /><Route path="*" element={<main className="state"><h1>Page not found</h1><Link to="/tickets">Return to workspace</Link></main>} /></Routes>; }
