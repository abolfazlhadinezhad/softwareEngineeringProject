import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { useAuth } from '../features/auth/AuthProvider';
import {
  Alert,
  Badge,
  BackLink,
  ErrorState,
  Field,
  Loading,
  PageHeader,
  date,
  label,
} from '../components/ui';
import { usePublic } from './PublicPages';
import TicketAttachments from '../components/TicketAttachments';

export default function TicketDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const client = useQueryClient();
  const [reply, setReply] = useState('');
  const [note, setNote] = useState('');
  const [reason, setReason] = useState('');
  const [department, setDepartment] = useState('');
  const [category, setCategory] = useState('');
  const [rating, setRating] = useState({
    overall: 5,
    speed: 5,
    quality: 5,
    solved: true,
    comment: '',
  });
  const query = useQuery({
    queryKey: ['ticket', id],
    queryFn: ({ signal }) => api('/tickets/' + id + '/', { signal }),
    refetchInterval: 15000,
  });
  const departments = usePublic('departments/');
  const categories = useQuery({ queryKey: ['categories'], queryFn: () => api('/categories/') });
  const mutation = useMutation({
    mutationFn: ({ action, body = {} }) =>
      api('/tickets/' + id + '/' + action + '/', { method: 'POST', body }),
    onSuccess: (_, variables) => {
      if (variables.action === 'reply') setReply('');
      if (variables.action === 'note') setNote('');
      ['ticket', 'tickets', 'metrics', 'dashboard', 'notifications'].forEach((key) =>
        client.invalidateQueries({ queryKey: [key] }),
      );
      if (variables.action === 'transfer') navigate('/tickets');
    },
  });
  if (query.isPending) return <Loading />;
  if (query.error)
    return (
      <>
        <BackLink />
        <ErrorState error={query.error} retry={query.refetch} />
      </>
    );
  const ticket = query.data;
  const staff = user.role !== 'student';
  const can = (action) => ticket.allowed_actions.permissions.includes(action);
  const send = (action, body) => mutation.mutate({ action, body });
  const disabled = mutation.isPending;
  return (
    <>
      <BackLink />
      <PageHeader eyebrow={'شماره پیگیری: ' + ticket.tracking_number} title={ticket.title}>
        <span className="detail-badges">
          <Badge value={ticket.status} />
          <Badge value={ticket.priority} />
        </span>
      </PageHeader>
      <Alert>{mutation.error?.message}</Alert>
      <div className="detail-grid">
        <div className="stack">
          <section className="panel panel-pad">
            <div className="message-head">
              <strong>{ticket.created_by.username} · دانشجو</strong>
              <small>{date(ticket.created_at)}</small>
            </div>
            <div className="pre-wrap">{ticket.description}</div>
            {ticket.form_snapshot.fields?.length > 0 && (
              <dl className="metadata">
                {ticket.form_snapshot.fields
                  .filter((f) => ticket.form_responses[f.key] != null)
                  .map((f) => (
                    <div key={f.key}>
                      <dt>{f.label}</dt>
                      <dd>{String(ticket.form_responses[f.key])}</dd>
                    </div>
                  ))}
              </dl>
            )}
          </section>
          <section className="panel panel-pad">
            <h2>گفت‌وگو · {ticket.replies.length} پیام</h2>
            {!ticket.replies.length && <p>هنوز پاسخی ثبت نشده است.</p>}
            {ticket.replies.map((message) => (
              <article className="message" key={message.id}>
                <div className="message-head">
                  <strong>
                    {message.author.username} · {label(message.author.role)}
                  </strong>
                  <small>{date(message.created_at)}</small>
                </div>
                <div className="pre-wrap">{message.body}</div>
              </article>
            ))}
            {!['closed', 'resolved'].includes(ticket.status) && can('reply') && (
              <form
                className="reply-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  send('reply', { body: reply });
                }}
              >
                <Field label="پاسخ" name="reply">
                  <textarea
                    id="reply"
                    maxLength={10000}
                    required
                    value={reply}
                    onChange={(e) => setReply(e.target.value)}
                  />
                </Field>
                <button disabled={disabled}>ارسال پاسخ</button>
              </form>
            )}
            {ticket.resolution_summary && (
              <div className="hint-panel">
                <strong>نتیجه رسیدگی</strong>
                <p className="pre-wrap">{ticket.resolution_summary}</p>
              </div>
            )}
          </section>
          <TicketAttachments ticket={ticket} />
          {staff && can('add_internal_note') && (
            <section className="panel panel-pad">
              <h2>یادداشت‌های داخلی</h2>
              <p className="notice">فقط برای کارکنان مجاز؛ برای دانشجو ارسال نمی‌شود.</p>
              {ticket.internal_notes.map((n) => (
                <article className="internal-note" key={n.id}>
                  <strong>{n.author__username}</strong>
                  <div className="pre-wrap">{n.body}</div>
                  <small>{date(n.created_at)}</small>
                </article>
              ))}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  send('note', { body: note });
                }}
              >
                <Field label="یادداشت داخلی" name="note">
                  <textarea
                    id="note"
                    required
                    maxLength={10000}
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                  />
                </Field>
                <button disabled={disabled}>ذخیره یادداشت داخلی</button>
              </form>
            </section>
          )}
          {!staff && ['resolved', 'closed'].includes(ticket.status) && (
            <section className="panel panel-pad">
              <h2>ارزیابی پشتیبانی</h2>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  send('feedback', rating);
                }}
              >
                <div className="form-grid">
                  {[
                    ['overall', 'رضایت کلی'],
                    ['speed', 'سرعت پاسخگویی'],
                    ['quality', 'کیفیت پاسخ'],
                  ].map(([key, title]) => (
                    <Field label={title} name={key} key={key}>
                      <select
                        id={key}
                        value={rating[key]}
                        onChange={(e) => setRating({ ...rating, [key]: Number(e.target.value) })}
                      >
                        {[5, 4, 3, 2, 1].map((n) => (
                          <option key={n} value={n}>
                            {n} از ۵
                          </option>
                        ))}
                      </select>
                    </Field>
                  ))}
                </div>
                <label className="check-label">
                  <input
                    type="checkbox"
                    checked={rating.solved}
                    onChange={(e) => setRating({ ...rating, solved: e.target.checked })}
                  />
                  مسئله من حل شده است
                </label>
                <Field label="نظر شما (اختیاری)" name="comment">
                  <textarea
                    id="comment"
                    maxLength={2000}
                    value={rating.comment}
                    onChange={(e) => setRating({ ...rating, comment: e.target.value })}
                  />
                </Field>
                <button disabled={disabled}>ثبت ارزیابی</button>
                {mutation.isSuccess && mutation.variables?.action === 'feedback' && (
                  <p role="status">ارزیابی ثبت شد.</p>
                )}
              </form>
            </section>
          )}
        </div>
        <aside className="stack">
          <section className="panel panel-pad">
            <h2>مشخصات درخواست</h2>
            <dl className="metadata">
              <div>
                <dt>دسته</dt>
                <dd>{ticket.category.name}</dd>
              </div>
              <div>
                <dt>مسئول رسیدگی</dt>
                <dd>{ticket.assignee?.username || 'بدون مسئول'}</dd>
              </div>
              <div>
                <dt>مهلت اولین پاسخ</dt>
                <dd>{date(ticket.response_due_at)}</dd>
              </div>
              <div>
                <dt>مهلت حل</dt>
                <dd>{date(ticket.resolution_due_at)}</dd>
              </div>
              <div>
                <dt>آخرین فعالیت</dt>
                <dd>{date(ticket.updated_at)}</dd>
              </div>
            </dl>
          </section>
          <section className="panel panel-pad">
            <h2>عملیات رسیدگی</h2>
            <div className="action-stack">
              {staff && can('assign') && !ticket.assignee && ticket.status === 'open' && (
                <button disabled={disabled} onClick={() => send('claim')}>
                  دریافت درخواست
                </button>
              )}
              {((staff && can('reply')) || ['resolved', 'closed'].includes(ticket.status)) && (
                <Field label="دلیل عملیات / نتیجه رسیدگی" name="reason">
                  <textarea
                    id="reason"
                    maxLength={2000}
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                  />
                </Field>
              )}
              {staff &&
                ticket.allowed_actions.transitions
                  .filter(
                    (s) =>
                      s !== 'closed' &&
                      can(s === 'resolved' ? 'resolve' : s === 'open' ? 'reopen' : 'reply'),
                  )
                  .map((s) => (
                    <button
                      className="secondary"
                      key={s}
                      disabled={disabled || (['resolved', 'open'].includes(s) && !reason.trim())}
                      onClick={() => send('status', { status: s, reason })}
                    >
                      {label(s)}
                    </button>
                  ))}
              {staff &&
                can('assign') &&
                ticket.assignee?.id === user.id &&
                ticket.status === 'in_progress' && (
                  <button
                    className="secondary"
                    disabled={disabled || !reason.trim()}
                    onClick={() => send('release', { reason })}
                  >
                    بازگرداندن به صف
                  </button>
                )}
              {!staff && ticket.status === 'resolved' && (
                <button disabled={disabled} onClick={() => send('close')}>
                  تأیید حل مسئله
                </button>
              )}
              {['resolved', 'closed'].includes(ticket.status) && can('reopen') && (
                <button
                  className="secondary"
                  disabled={disabled || !reason.trim()}
                  onClick={() => send('reopen', { reason })}
                >
                  درخواست بازگشایی
                </button>
              )}
              {staff && ticket.status === 'resolved' && can('close') && (
                <button
                  className="secondary"
                  disabled={disabled || !reason.trim()}
                  onClick={() => send('close', { reason })}
                >
                  بستن درخواست
                </button>
              )}
            </div>
          </section>
          {staff && can('transfer') && !['closed', 'resolved'].includes(ticket.status) && (
            <section className="panel panel-pad">
              <h2>انتقال به واحد مسئول</h2>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  send('transfer', { department, category, reason });
                }}
              >
                <Field label="واحد مقصد" name="target">
                  <select
                    id="target"
                    required
                    value={department}
                    onChange={(e) => {
                      setDepartment(e.target.value);
                      setCategory('');
                    }}
                  >
                    <option value="">انتخاب واحد</option>
                    {departments.data?.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="دسته مقصد" name="target-category">
                  <select
                    id="target-category"
                    required
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  >
                    <option value="">انتخاب دسته</option>
                    {categories.data
                      ?.filter((c) => String(c.department) === department)
                      .map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name}
                        </option>
                      ))}
                  </select>
                </Field>
                <p className="notice">
                  دلیل انتقال را در بخش عملیات وارد کنید. پس از انتقال ممکن است دسترسی شما پایان
                  یابد.
                </p>
                <button disabled={disabled || !reason.trim()}>انتقال درخواست</button>
              </form>
            </section>
          )}
          <section className="panel panel-pad">
            <h2>تاریخچه رسیدگی</h2>
            <ul className="activity">
              {ticket.events.map((event) => (
                <li key={event.id}>
                  <strong>{label(event.action)}</strong>
                  <br />
                  {event.detail}
                  <small>
                    {event.actor?.username || 'سامانه'} · {date(event.created_at)}
                  </small>
                </li>
              ))}
            </ul>
          </section>
        </aside>
      </div>
    </>
  );
}
