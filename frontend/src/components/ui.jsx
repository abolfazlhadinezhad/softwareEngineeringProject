import { Link } from 'react-router-dom';

export const label = value => value?.replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'Unassigned';
export const date = value => new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
export function Badge({ value }) { return <span className={`badge badge-${value}`}>{label(value)}</span>; }
export function Alert({ children }) { return children ? <div role="alert" className="alert">{children}</div> : null; }
export function Loading({ children = 'Loading…' }) { return <div role="status" className="state"><span className="spinner" />{children}</div>; }
export function ErrorState({ error, retry }) { return <div className="panel state"><h2>Unable to load this page</h2><p role="alert">{error?.message || 'Please check your connection.'}</p>{retry && <button onClick={() => retry()}>Try again</button>}</div>; }
export function EmptyState({ title, children }) { return <div className="state"><div className="empty-icon" aria-hidden="true">↗</div><h2>{title}</h2><p>{children}</p></div>; }
export function PageHeader({ eyebrow, title, children, action }) { return <header className="page-header"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{children && <p>{children}</p>}</div>{action}</header>; }
export function Field({ label: text, name, error, children, hint }) { return <div className="field"><label htmlFor={name}>{text}</label>{children}{hint && <small id={`${name}-hint`}>{hint}</small>}{error && <small className="field-error" id={`${name}-error`}>{Array.isArray(error) ? error.join(' ') : error}</small>}</div>; }
export function Pagination({ data, page, onPage }) { return data && data.count > 20 ? <nav className="pagination" aria-label="Pagination"><button className="secondary" disabled={!data.previous} onClick={() => onPage(page - 1)}>Previous</button><span>Page {page} · {data.count} results</span><button className="secondary" disabled={!data.next} onClick={() => onPage(page + 1)}>Next</button></nav> : null; }
export function BackLink() { return <Link className="back-link" to="/tickets">← All tickets</Link>; }
