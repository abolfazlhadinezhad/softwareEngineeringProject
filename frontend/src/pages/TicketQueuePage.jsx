import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { useAuth } from '../features/auth/AuthProvider';
import { Alert, Badge, EmptyState, ErrorState, Field, Loading, PageHeader, Pagination, date, label } from '../components/ui';

const statuses = ['', 'open', 'in_progress', 'waiting_student', 'resolved', 'closed'];
const priorities = ['', 'low', 'normal', 'high'];

function useTicketData(params) {
  const query = params.toString();
  return useQuery({ queryKey: ['tickets', query], queryFn: () => api(`/tickets/${query ? `?${query}` : ''}`), keepPreviousData: true });
}

export default function TicketQueuePage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [draft, setDraft] = useState({ search: searchParams.get('search') || '', status: searchParams.get('status') || '', priority: searchParams.get('priority') || '', category: searchParams.get('category') || '' });
  const query = useTicketData(searchParams);
  const categories = useQuery({ queryKey: ['categories'], queryFn: () => api('/categories/') });
  const metrics = useQuery({ queryKey: ['metrics'], queryFn: () => api('/metrics/') });
  const page = Number(searchParams.get('page') || 1);
  const hasFilters = [...searchParams.keys()].length > 0;
  const emptyText = user.role === 'student' ? 'Tickets you submit will appear here.' : 'New student requests will appear in the shared queue.';
  const selectedCategory = useMemo(() => new Map((categories.data || []).map(item => [String(item.id), item.name])), [categories.data]);
  function apply(event) { event.preventDefault(); const next = new URLSearchParams(); Object.entries(draft).forEach(([key, value]) => value && next.set(key, value)); setSearchParams(next); }
  function clear() { setDraft({ search: '', status: '', priority: '', category: '' }); setSearchParams({}); }
  function paginate(nextPage) { const next = new URLSearchParams(searchParams); next.set('page', nextPage); setSearchParams(next); }
  if (query.isPending || categories.isPending || metrics.isPending) return <Loading>Loading your support workspace…</Loading>;
  if (query.error || categories.error || metrics.error) return <ErrorState error={query.error || categories.error || metrics.error} retry={() => { query.refetch(); categories.refetch(); metrics.refetch(); }} />;
  const rows = query.data?.results || [];
  return <>
    <PageHeader eyebrow={user.role === 'student' ? 'YOUR SUPPORT WORKSPACE' : 'UNIVERSITY SUPPORT QUEUE'} title={user.role === 'student' ? 'Your tickets.' : 'Support queue.'} action={user.role === 'student' && <Link className="button" to="/tickets/new">＋ New ticket</Link>}>
      {user.role === 'student' ? 'Keep track of your requests and every reply in one place.' : 'Review, claim, and move student requests toward resolution.'}
    </PageHeader>
    <div className="stats"><div className="panel stat"><div><span className="stat-label">ALL TICKETS</span><strong>{metrics.data.all}</strong></div><span className="stat-symbol">▦</span></div><div className="panel stat"><div><span className="stat-label">ACTIVE</span><strong>{metrics.data.active}</strong></div><span className="stat-symbol">◌</span></div><div className="panel stat"><div><span className="stat-label">CLOSED</span><strong>{metrics.data.closed}</strong></div><span className="stat-symbol">✓</span></div></div>
    <section className="panel">
      <div className="section-top"><div><h2>{user.role === 'student' ? 'Your requests' : 'All student requests'}</h2><small>{query.data.count} {query.data.count === 1 ? 'ticket' : 'tickets'} in your view</small></div>{hasFilters && <button className="secondary" onClick={clear}>Clear filters</button>}</div>
      <form className="filters" onSubmit={apply}><Field label="Search" name="ticket-search"><input id="ticket-search" value={draft.search} onChange={event => setDraft({ ...draft, search: event.target.value })} placeholder="Title or description" /></Field><Field label="Status" name="ticket-status"><select id="ticket-status" value={draft.status} onChange={event => setDraft({ ...draft, status: event.target.value })}>{statuses.map(value => <option key={value} value={value}>{value ? label(value) : 'All statuses'}</option>)}</select></Field><Field label="Priority" name="ticket-priority"><select id="ticket-priority" value={draft.priority} onChange={event => setDraft({ ...draft, priority: event.target.value })}>{priorities.map(value => <option key={value} value={value}>{value ? label(value) : 'All priorities'}</option>)}</select></Field><Field label="Category" name="ticket-category"><select id="ticket-category" value={draft.category} onChange={event => setDraft({ ...draft, category: event.target.value })}><option value="">All categories</option>{categories.data.map(category => <option key={category.id} value={category.id}>{category.name}</option>)}</select></Field><button type="submit">Apply</button></form>
      {query.isFetching && <div className="notice" style={{ padding: '0 24px' }}>Updating results…</div>}
      {rows.length === 0 ? <EmptyState title={hasFilters ? 'No matching tickets' : 'Nothing here yet'}>{hasFilters ? <button className="secondary" onClick={clear}>Clear filters</button> : emptyText}</EmptyState> : <><div className="table-region"><table><thead><tr><th>Ticket</th><th>Status</th><th>Priority</th><th>Category</th><th>{user.role === 'student' ? 'Updated' : 'Assignee'}</th></tr></thead><tbody>{rows.map(ticket => <tr key={ticket.id}><td className="ticket-title"><Link to={`/tickets/${ticket.id}`}>#{ticket.id} · {ticket.title}</Link><small>{date(ticket.created_at)}</small></td><td><Badge value={ticket.status} /></td><td><Badge value={ticket.priority} /></td><td>{selectedCategory.get(String(ticket.category.id)) || ticket.category.name}</td><td>{user.role === 'student' ? date(ticket.updated_at) : ticket.assignee?.username || <span className="note">Unassigned</span>}</td></tr>)}</tbody></table></div><Pagination data={query.data} page={page} onPage={paginate} /></>}
    </section>
  </>;
}
