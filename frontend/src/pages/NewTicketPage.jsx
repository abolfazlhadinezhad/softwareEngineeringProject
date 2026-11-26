import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Alert, ErrorState, Field, Loading, PageHeader } from '../components/ui';

export default function NewTicketPage() {
  const navigate = useNavigate();
  const categories = useQuery({ queryKey: ['categories'], queryFn: () => api('/categories/') });
  const [form, setForm] = useState({ title: '', category: '', priority: 'normal', description: '' });
  const [error, setError] = useState(null);
  const mutation = useMutation({ mutationFn: body => api('/tickets/', { method: 'POST', body }), onSuccess: ticket => navigate(`/tickets/${ticket.id}`), onError: setError });
  function submit(event) { event.preventDefault(); setError(null); mutation.mutate(form); }
  if (categories.isPending) return <Loading>Loading ticket categories…</Loading>;
  if (categories.error) return <ErrorState error={categories.error} retry={categories.refetch} />;
  return <div className="form-wrap"><Link className="back-link" to="/tickets">← All tickets</Link><PageHeader eyebrow="NEW REQUEST" title="Tell us how we can help." >Give your request a clear title and enough context for the right support team to respond.</PageHeader>{categories.data.length === 0 && <div className="hint-panel"><strong>No categories are available yet.</strong><p className="notice">Ask an administrator to activate a support category before submitting.</p></div>}<form className="panel panel-pad" onSubmit={submit}><Alert>{error?.message}</Alert><Field label="Title" name="title" hint={`${form.title.length}/160 characters`}><input id="title" required maxLength={160} value={form.title} onChange={event => setForm({ ...form, title: event.target.value })} /></Field><div className="form-grid"><Field label="Category" name="category"><select id="category" required value={form.category} onChange={event => setForm({ ...form, category: event.target.value })}><option value="">Choose a category</option>{categories.data.map(category => <option key={category.id} value={category.id}>{category.name}</option>)}</select></Field><Field label="Priority" name="priority"><select id="priority" value={form.priority} onChange={event => setForm({ ...form, priority: event.target.value })}><option value="low">Low</option><option value="normal">Normal</option><option value="high">High</option></select></Field></div><Field label="Description" name="description" hint={`${form.description.length}/10,000 characters`}><textarea id="description" required maxLength={10000} value={form.description} onChange={event => setForm({ ...form, description: event.target.value })} placeholder="What happened, and what would a helpful answer look like?" /></Field><div className="form-actions"><button disabled={mutation.isPending || categories.data.length === 0}>{mutation.isPending ? 'Submitting…' : 'Submit ticket →'}</button><Link to="/tickets">Cancel</Link></div></form></div>;
}
