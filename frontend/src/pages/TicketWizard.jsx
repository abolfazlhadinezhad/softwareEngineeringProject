import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { Alert, ErrorState, Field, Loading, PageHeader } from '../components/ui';
import DynamicFields from '../components/DynamicFields';
import { ArticleCards, usePublic } from './PublicPages';

export default function TicketWizard() {
  const navigate = useNavigate();
  const client = useQueryClient();
  const [params] = useSearchParams();
  const [step, setStep] = useState(0);
  const [department, setDepartment] = useState(params.get('department') || '');
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: '',
    form_responses: {},
  });
  const departments = usePublic('departments/');
  const categories = useQuery({ queryKey: ['categories'], queryFn: () => api('/categories/') });
  const suggestions = usePublic('articles/?q=' + encodeURIComponent(form.title));
  const mutation = useMutation({
    mutationFn: () => api('/tickets/', { method: 'POST', body: form }),
    onSuccess: (ticket) => {
      client.invalidateQueries({ queryKey: ['tickets'] });
      client.invalidateQueries({ queryKey: ['dashboard'] });
      navigate('/tickets/' + ticket.id);
    },
  });
  if (departments.isPending || categories.isPending) return <Loading />;
  if (departments.error || categories.error)
    return (
      <ErrorState
        error={departments.error || categories.error}
        retry={() => {
          departments.refetch();
          categories.refetch();
        }}
      />
    );
  const selected = categories.data.find((c) => String(c.id) === String(form.category));
  const steps = ['شرح موضوع', 'بررسی راهنماها', 'واحد و فرم درخواست', 'بازبینی و ارسال'];
  return (
    <div className="form-wrap">
      <PageHeader eyebrow="ثبت درخواست" title="با هم مسیر رسیدگی را مشخص کنیم" />
      <ol className="wizard-steps">
        {steps.map((s, i) => (
          <li
            key={s}
            aria-current={i === step ? 'step' : undefined}
            className={i <= step ? 'current' : ''}
          >
            {i + 1}. {s}
          </li>
        ))}
      </ol>
      <Alert>{mutation.error?.message}</Alert>
      <form
        className="panel panel-pad"
        onSubmit={(e) => {
          e.preventDefault();
          if (step < 3) setStep(step + 1);
          else mutation.mutate();
        }}
      >
        {step === 0 && (
          <>
            <h2>چه کمکی نیاز دارید؟</h2>
            <Field label="موضوع درخواست" name="title">
              <input
                id="title"
                required
                maxLength={160}
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
            </Field>
            <p className="notice">رمز عبور، کد ملی یا اطلاعات غیرضروری را در درخواست وارد نکنید.</p>
          </>
        )}
        {step === 1 && (
          <>
            <h2>ممکن است پاسخ شما اینجا باشد</h2>
            {suggestions.isPending ? (
              <Loading />
            ) : suggestions.error ? (
              <ErrorState error={suggestions.error} retry={suggestions.refetch} />
            ) : suggestions.data.results.length ? (
              <ArticleCards articles={suggestions.data.results.slice(0, 3)} />
            ) : (
              <p>راهنمای مرتبطی پیدا نشد؛ درخواست خود را ادامه دهید.</p>
            )}
          </>
        )}
        {step === 2 && (
          <>
            <Field label="واحد مسئول" name="department">
              <select
                id="department"
                required
                value={department}
                onChange={(e) => {
                  setDepartment(e.target.value);
                  setForm({ ...form, category: '', form_responses: {} });
                }}
              >
                <option value="">انتخاب واحد</option>
                {departments.data.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="دسته‌بندی" name="category">
              <select
                id="category"
                required
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value, form_responses: {} })}
              >
                <option value="">انتخاب دسته</option>
                {categories.data
                  .filter((c) => String(c.department) === String(department))
                  .map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
              </select>
            </Field>
            <DynamicFields
              fields={selected?.form?.fields}
              value={form.form_responses}
              onChange={(form_responses) => setForm({ ...form, form_responses })}
            />
            <Field label="شرح درخواست" name="description">
              <textarea
                id="description"
                required
                maxLength={10000}
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </Field>
          </>
        )}
        {step === 3 && (
          <>
            <h2>بازبینی درخواست</h2>
            <dl className="metadata">
              <div>
                <dt>موضوع</dt>
                <dd>{form.title}</dd>
              </div>
              <div>
                <dt>واحد</dt>
                <dd>{departments.data.find((d) => String(d.id) === department)?.name}</dd>
              </div>
              <div>
                <dt>دسته</dt>
                <dd>{selected?.name}</dd>
              </div>
            </dl>
            <div className="pre-wrap">{form.description}</div>
            <p className="notice">
              اولویت نهایی طبق سیاست واحد مسئول تعیین می‌شود. پس از ارسال، شماره پیگیری اختصاصی
              دریافت می‌کنید.
            </p>
          </>
        )}
        <div className="form-actions">
          {step > 0 && (
            <button
              type="button"
              className="secondary"
              disabled={mutation.isPending}
              onClick={() => setStep(step - 1)}
            >
              مرحله قبل
            </button>
          )}
          <button disabled={mutation.isPending}>
            {mutation.isPending ? 'در حال ثبت…' : step < 3 ? 'ادامه ←' : 'ثبت نهایی درخواست'}
          </button>
          <Link to="/tickets">انصراف</Link>
        </div>
      </form>
    </div>
  );
}
