import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Alert, EmptyState, ErrorState, Field, Loading, PageHeader, date } from '../components/ui';

export const resources = {
  departments: [
    'واحدهای سازمانی',
    [
      'name',
      'english_name',
      'slug',
      'description',
      'parent',
      'email',
      'phone',
      'business_hours',
      'is_active',
      'is_public',
      'confidentiality',
    ],
  ],
  categories: [
    'دسته‌بندی درخواست‌ها',
    ['name', 'department', 'parent', 'form', 'sla_policy', 'default_priority', 'is_active'],
  ],
  forms: ['فرم‌های درخواست', ['name', 'department', 'fields', 'is_active']],
  roles: ['نقش‌ها و مجوزها', ['name', 'slug', 'description', 'permissions']],
  'role-assignments': ['تخصیص نقش', ['user', 'role', 'department']],
  memberships: ['عضویت کارکنان', ['user', 'department', 'job_title', 'is_manager', 'availability']],
  articles: [
    'مقالات مرکز راهنما',
    [
      'title',
      'slug',
      'summary',
      'content',
      'category',
      'department',
      'tags',
      'status',
      'is_public',
      'published_at',
    ],
  ],
  faqs: [
    'پرسش‌های متداول',
    ['question', 'answer', 'category', 'department', 'article', 'is_published', 'ordering'],
  ],
  announcements: [
    'اطلاعیه‌ها',
    [
      'title',
      'content',
      'department',
      'priority',
      'audience',
      'is_published',
      'pinned',
      'starts_at',
      'expires_at',
    ],
  ],
  calendars: ['تقویم‌های کاری', ['name', 'timezone', 'weekdays', 'opens', 'closes']],
  holidays: ['تعطیلات', ['calendar', 'date', 'name']],
  'sla-policies': [
    'سیاست‌های پاسخگویی',
    [
      'name',
      'calendar',
      'first_response_minutes',
      'resolution_minutes',
      'warning_minutes',
      'pause_waiting_student',
    ],
  ],
};
const names = {
  name: 'نام',
  english_name: 'نام انگلیسی',
  slug: 'شناسه یکتا',
  description: 'توضیحات',
  parent: 'شناسه والد',
  email: 'ایمیل',
  phone: 'تلفن',
  business_hours: 'ساعات پاسخگویی',
  is_active: 'فعال',
  is_public: 'نمایش عمومی',
  confidentiality: 'سطح محرمانگی',
  department: 'شناسه واحد',
  form: 'شناسه فرم',
  sla_policy: 'شناسه سیاست SLA',
  default_priority: 'اولویت پیش‌فرض',
  fields: 'فیلدهای فرم',
  permissions: 'مجوزها',
  user: 'شناسه کاربر',
  role: 'شناسه نقش',
  job_title: 'عنوان شغلی',
  is_manager: 'مدیر واحد',
  availability: 'وضعیت حضور',
  title: 'عنوان',
  summary: 'خلاصه',
  content: 'متن',
  category: 'دسته',
  tags: 'برچسب‌ها (JSON)',
  status: 'وضعیت',
  published_at: 'زمان انتشار (با منطقه زمانی)',
  question: 'پرسش',
  answer: 'پاسخ',
  article: 'شناسه مقاله مرتبط',
  is_published: 'منتشر شده',
  ordering: 'ترتیب',
  priority: 'اهمیت',
  audience: 'مخاطبان',
  pinned: 'سنجاق شده',
  starts_at: 'شروع نمایش',
  expires_at: 'پایان نمایش',
  timezone: 'منطقه زمانی',
  weekdays: 'روزهای کاری (JSON؛ دوشنبه=۰)',
  opens: 'شروع ساعت کاری',
  closes: 'پایان ساعت کاری',
  calendar: 'شناسه تقویم',
  date: 'تاریخ',
  first_response_minutes: 'مهلت اولین پاسخ (دقیقه کاری)',
  resolution_minutes: 'مهلت حل (دقیقه کاری)',
  warning_minutes: 'آستانه هشدار (دقیقه)',
  pause_waiting_student: 'توقف مهلت حل هنگام انتظار دانشجو',
};
const jsonFields = ['tags', 'permissions', 'weekdays'];

function FormBuilder({ value, onChange }) {
  const fields = value || [];
  const update = (i, patch) => onChange(fields.map((f, j) => (i === j ? { ...f, ...patch } : f)));
  return (
    <div className="form-builder">
      {fields.map((f, i) => (
        <fieldset key={i}>
          <legend>فیلد {i + 1}</legend>
          <div className="form-grid">
            <Field name={'key-' + i} label="شناسه فیلد">
              <input
                id={'key-' + i}
                required
                value={f.key}
                onChange={(e) => update(i, { key: e.target.value })}
              />
            </Field>
            <Field name={'label-' + i} label="عنوان فیلد">
              <input
                id={'label-' + i}
                required
                value={f.label}
                onChange={(e) => update(i, { label: e.target.value })}
              />
            </Field>
            <Field name={'type-' + i} label="نوع">
              <select
                id={'type-' + i}
                value={f.type}
                onChange={(e) => update(i, { type: e.target.value })}
              >
                {[
                  ['text', 'متن کوتاه'],
                  ['textarea', 'متن بلند'],
                  ['number', 'عدد'],
                  ['select', 'انتخاب'],
                  ['multiselect', 'چندانتخابی'],
                  ['radio', 'گزینه'],
                  ['checkbox', 'بله/خیر'],
                  ['date', 'تاریخ'],
                  ['time', 'ساعت'],
                ].map(([v, l]) => (
                  <option value={v} key={v}>
                    {l}
                  </option>
                ))}
              </select>
            </Field>
            <label className="check-label">
              <input
                type="checkbox"
                checked={!!f.required}
                onChange={(e) => update(i, { required: e.target.checked })}
              />
              الزامی
            </label>
          </div>
          {['select', 'multiselect', 'radio'].includes(f.type) && (
            <Field name={'options-' + i} label="گزینه‌ها؛ هر گزینه یک خط">
              <textarea
                id={'options-' + i}
                value={(f.options || []).join('\n')}
                onChange={(e) => update(i, { options: e.target.value.split('\n') })}
              />
            </Field>
          )}
          <button
            type="button"
            className="secondary"
            onClick={() => onChange(fields.filter((_, j) => j !== i))}
          >
            حذف فیلد
          </button>
        </fieldset>
      ))}
      <button
        type="button"
        className="secondary"
        onClick={() =>
          onChange([
            ...fields,
            { key: 'field_' + (fields.length + 1), label: '', type: 'text', required: false },
          ])
        }
      >
        ＋ افزودن فیلد
      </button>
    </div>
  );
}

export default function AdminResourcePage() {
  const { resource } = useParams();
  const definition = resources[resource];
  const [selected, setSelected] = useState(null);
  const [values, setValues] = useState({});
  const [page, setPage] = useState(1);
  const [localError, setLocalError] = useState('');
  const path = '/manage/' + resource + '/';
  const query = useQuery({
    queryKey: ['manage', resource, page],
    queryFn: () => api(path + '?page=' + page),
    enabled: !!definition,
  });
  const schema = useQuery({
    queryKey: ['manage-schema', resource],
    queryFn: () => api(path + 'form-metadata/'),
    enabled: !!definition,
  });
  const mutation = useMutation({
    mutationFn: (body) =>
      api(path + (selected ? selected.id + '/' : ''), {
        method: selected ? 'PATCH' : 'POST',
        body,
      }),
    onSuccess: () => {
      setSelected(null);
      setValues({});
      query.refetch();
    },
  });
  useEffect(() => {
    setSelected(null);
    setValues({});
    setPage(1);
    setLocalError('');
    mutation.reset();
  }, [resource]);
  if (!definition)
    return (
      <EmptyState title="صفحه مدیریت یافت نشد">
        <Link to="/dashboard">بازگشت</Link>
      </EmptyState>
    );
  if (query.isPending || schema.isPending) return <Loading />;
  if (query.error || schema.error)
    return (
      <ErrorState
        error={query.error || schema.error}
        retry={() => {
          query.refetch();
          schema.refetch();
        }}
      />
    );
  const [title, fields] = definition;
  const metadata = schema.data.actions?.POST || {};
  function submit(e) {
    e.preventDefault();
    setLocalError('');
    try {
      const body = { ...values };
      for (const key of jsonFields)
        if (typeof body[key] === 'string') body[key] = JSON.parse(body[key] || '[]');
      mutation.mutate(body);
    } catch {
      setLocalError('ساختار JSON معتبر نیست.');
    }
  }
  return (
    <>
      <PageHeader eyebrow="مدیریت سامانه" title={title} />
      <div className="manage-grid">
        <section className="panel panel-pad">
          <h2>فهرست · {query.data.count} مورد</h2>
          {query.data.results.length ? (
            query.data.results.map((row) => (
              <button
                className="resource-row"
                key={row.id}
                onClick={() => {
                  setSelected(row);
                  setValues(
                    Object.fromEntries(
                      fields.map((k) => [
                        k,
                        jsonFields.includes(k) ? JSON.stringify(row[k] ?? []) : row[k],
                      ]),
                    ),
                  );
                  mutation.reset();
                }}
              >
                <span>{row.name || row.title || row.question || 'رکورد ' + row.id}</span>
                <small>#{row.id} · ویرایش</small>
              </button>
            ))
          ) : (
            <EmptyState title="هنوز موردی ثبت نشده است" />
          )}
          <div className="pagination">
            <button disabled={!query.data.previous} onClick={() => setPage(page - 1)}>
              قبلی
            </button>
            <span>{page}</span>
            <button disabled={!query.data.next} onClick={() => setPage(page + 1)}>
              بعدی
            </button>
          </div>
        </section>
        <form className="panel panel-pad" onSubmit={submit}>
          <h2>{selected ? 'ویرایش #' + selected.id : 'ایجاد مورد جدید'}</h2>
          <Alert>{mutation.error?.message || localError}</Alert>
          {mutation.isSuccess && <p role="status">اطلاعات ذخیره شد.</p>}
          {fields.map((key) => {
            const meta = metadata[key] || {};
            const value = values[key] ?? '';
            const props = {
              id: key,
              required: !selected && meta.required,
              value,
              onChange: (e) =>
                setValues({
                  ...values,
                  [key]: e.target.value === '' && meta.allow_null ? null : e.target.value,
                }),
            };
            return (
              <Field key={key} name={key} label={names[key] || key}>
                {key === 'fields' ? (
                  <FormBuilder
                    value={values.fields}
                    onChange={(fields) => setValues({ ...values, fields })}
                  />
                ) : meta.type === 'boolean' ? (
                  <input
                    id={key}
                    type="checkbox"
                    checked={!!values[key]}
                    onChange={(e) => setValues({ ...values, [key]: e.target.checked })}
                  />
                ) : meta.choices ? (
                  <select {...props}>
                    <option value="">انتخاب</option>
                    {meta.choices.map((c) => (
                      <option key={c.value} value={c.value}>
                        {c.display_name}
                      </option>
                    ))}
                  </select>
                ) : ['description', 'content', 'summary', 'answer', ...jsonFields].includes(key) ? (
                  <textarea {...props} rows={key === 'content' ? 10 : 3} />
                ) : (
                  <input
                    {...props}
                    type={
                      meta.type === 'integer' || meta.type === 'field'
                        ? 'number'
                        : key === 'email'
                          ? 'email'
                          : key === 'date'
                            ? 'date'
                            : ['opens', 'closes'].includes(key)
                              ? 'time'
                              : 'text'
                    }
                  />
                )}
              </Field>
            );
          })}
          <div className="form-actions">
            <button disabled={mutation.isPending}>
              {mutation.isPending ? 'در حال ذخیره…' : 'ذخیره'}
            </button>
            {selected && (
              <button
                type="button"
                className="secondary"
                onClick={() => {
                  setSelected(null);
                  setValues({});
                }}
              >
                ایجاد مورد جدید
              </button>
            )}
          </div>
        </form>
      </div>
    </>
  );
}

export function AuditPage() {
  const query = useQuery({ queryKey: ['audit'], queryFn: () => api('/manage/audit/') });
  if (query.isPending) return <Loading />;
  if (query.error) return <ErrorState error={query.error} retry={query.refetch} />;
  return (
    <>
      <PageHeader title="سوابق ممیزی" />
      <div className="panel table-region">
        <table>
          <thead>
            <tr>
              <th>عملیات</th>
              <th>منبع</th>
              <th>کاربر</th>
              <th>زمان</th>
            </tr>
          </thead>
          <tbody>
            {query.data.results.map((r) => (
              <tr key={r.id}>
                <td>{r.action}</td>
                <td>{r.resource}</td>
                <td>{r.actor}</td>
                <td>{date(r.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
