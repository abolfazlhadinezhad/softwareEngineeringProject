import { Link, Outlet, useParams, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { EmptyState, ErrorState, Loading, PageHeader, date } from '../components/ui';

export function PublicLayout() {
  return (
    <div className="public-site">
      <a className="skip-link" href="#main">
        رفتن به محتوا
      </a>
      <header className="public-nav">
        <Link className="brand" to="/">
          <span className="brand-mark">ن</span>
          <span>
            دانشگاه صنعتی نوشیروانی بابل
            <small className="brand-sub">سامانه پاسخگویی و پشتیبانی دانشجویان</small>
          </span>
        </Link>
        <nav aria-label="راهبری عمومی">
          <Link to="/knowledge">مرکز راهنما</Link>
          <Link to="/faq">پرسش‌های متداول</Link>
          <Link to="/departments">واحدها</Link>
          <Link to="/announcements">اطلاعیه‌ها</Link>
          <Link className="button" to="/login">
            ورود دانشجو
          </Link>
          <Link to="/staff/login">ورود کارکنان</Link>
        </nav>
      </header>
      <main id="main" className="public-main">
        <Outlet />
      </main>
      <footer className="public-footer">
        <span>سامانه پشتیبانی BNUT · هویت بصری موقت و قابل تنظیم</span>
        <nav>
          <Link to="/about">درباره سامانه</Link>
          <Link to="/privacy">حریم خصوصی</Link>
          <Link to="/accessibility">دسترس‌پذیری</Link>
        </nav>
      </footer>
    </div>
  );
}

export function usePublic(resource) {
  return useQuery({
    queryKey: ['public', resource],
    queryFn: ({ signal }) => api('/public/' + resource, { signal }),
    staleTime: 30000,
  });
}

function RequestState({ query, children }) {
  if (query.isPending) return <Loading />;
  if (query.error) return <ErrorState error={query.error} retry={query.refetch} />;
  return children(query.data);
}

export function SearchBox({ initial = '' }) {
  return (
    <form className="help-search" action="/knowledge">
      <label className="sr-only" htmlFor="help-q">
        جستجو در راهنما
      </label>
      <input
        id="help-q"
        name="q"
        type="search"
        defaultValue={initial}
        placeholder="درباره چه موضوعی راهنمایی می‌خواهید؟"
        maxLength={120}
      />
      <button>جستجو</button>
    </form>
  );
}

export function ArticleCards({ articles }) {
  return (
    <div className="content-grid">
      {articles.map((a) => (
        <Link className="panel content-card" to={'/knowledge/' + a.id} key={a.id}>
          <span className="eyebrow">{a.category}</span>
          <h3>{a.title}</h3>
          <p>{a.summary}</p>
          <span className="text-link">مطالعه راهنما ←</span>
        </Link>
      ))}
    </div>
  );
}

export function HomePage() {
  const query = usePublic('');
  return (
    <RequestState query={query}>
      {(data) => (
        <>
          <section className="hero">
            <div className="eyebrow">راهنمای خدمات دانشگاه</div>
            <h1>
              پرسش شما،
              <br />
              مسیر روشن پاسخگویی.
            </h1>
            <p>
              پاسخ را در مرکز راهنما پیدا کنید؛ اگر به پیگیری نیاز دارید، درخواست خود را برای واحد
              مسئول بفرستید.
            </p>
            <SearchBox />
            <div className="hero-links">
              <Link to="/faq">پرسش‌های متداول</Link>
              <Link to="/tickets/new">ثبت و پیگیری درخواست ←</Link>
            </div>
          </section>
          <section className="public-section">
            <PageHeader title="از کجا شروع کنیم؟" />
            <div className="process-grid">
              {[
                ['۱', 'جستجوی پاسخ', 'راهنماها و پرسش‌های پرتکرار را مرور کنید.'],
                ['۲', 'انتخاب واحد مسئول', 'درخواست شما در صف واحد مرتبط قرار می‌گیرد.'],
                ['۳', 'پیگیری تا نتیجه', 'پاسخ‌ها و روند رسیدگی را در حساب خود ببینید.'],
              ].map(([n, t, d]) => (
                <div key={n}>
                  <span className="step-number">{n}</span>
                  <h3>{t}</h3>
                  <p>{d}</p>
                </div>
              ))}
            </div>
          </section>
          <section className="public-section">
            <PageHeader
              title="راهنماهای خدمات"
              action={<Link to="/knowledge">همه راهنماها ←</Link>}
            />
            <ArticleCards articles={data.articles} />
            {!data.articles.length && <EmptyState title="هنوز راهنمایی منتشر نشده است" />}
          </section>
          <section className="public-section">
            <PageHeader
              title="واحدهای پاسخگو"
              action={<Link to="/departments">فهرست واحدها ←</Link>}
            />
            <div className="department-grid">
              {data.departments.map((d) => (
                <Link key={d.id} to={'/departments/' + d.id} className="department-link">
                  <span aria-hidden="true">◈</span>
                  <strong>{d.name}</strong>
                  <span>←</span>
                </Link>
              ))}
            </div>
          </section>
          <section className="public-section">
            <PageHeader title="اطلاعیه‌های تازه" />
            <AnnouncementList rows={data.announcements} />
          </section>
          <aside className="support-strip">
            <strong>ساعات پاسخگویی</strong>
            <span>{data.settings.support_hours}</span>
            {data.settings.contact_email && (
              <a dir="ltr" href={'mailto:' + data.settings.contact_email}>
                {data.settings.contact_email}
              </a>
            )}
          </aside>
        </>
      )}
    </RequestState>
  );
}

export function KnowledgePage() {
  const [params, setParams] = useSearchParams();
  const query = usePublic('articles/?' + params.toString());
  return (
    <>
      <PageHeader eyebrow="مرکز راهنما" title="پاسخ نزدیک‌تر از چیزی است که فکر می‌کنید" />
      <SearchBox initial={params.get('q') || ''} />
      <RequestState query={query}>
        {(data) => (
          <>
            <p className="notice">{data.count.toLocaleString('fa-IR')} راهنما یافت شد</p>
            <ArticleCards articles={data.results} />
            {!data.count && (
              <EmptyState title="پاسخی برای این عبارت پیدا نشد">
                عبارت کوتاه‌تری امتحان کنید یا <Link to="/tickets/new">درخواست جدید ثبت کنید</Link>.
              </EmptyState>
            )}
            {(data.next || data.previous) && (
              <div className="pagination">
                <button
                  disabled={!data.previous}
                  onClick={() => {
                    const p = new URLSearchParams(params);
                    p.set('page', Number(params.get('page') || 1) - 1);
                    setParams(p);
                  }}
                >
                  قبلی
                </button>
                <button
                  disabled={!data.next}
                  onClick={() => {
                    const p = new URLSearchParams(params);
                    p.set('page', Number(params.get('page') || 1) + 1);
                    setParams(p);
                  }}
                >
                  بعدی
                </button>
              </div>
            )}
          </>
        )}
      </RequestState>
    </>
  );
}

export function ArticlePage() {
  const { id } = useParams();
  const query = usePublic('articles/' + id + '/');
  return (
    <RequestState query={query}>
      {(a) => (
        <article className="reading-page">
          <Link to="/knowledge">مرکز راهنما ←</Link>
          <PageHeader eyebrow={a.category} title={a.title} />
          <p className="notice">آخرین ویرایش: {date(a.updated_at)}</p>
          <p className="article-summary">{a.summary}</p>
          <div className="pre-wrap article-content">{a.content}</div>
          {a.related?.length > 0 && (
            <>
              <h2>راهنماهای مرتبط</h2>
              <ArticleCards articles={a.related} />
            </>
          )}
          <div className="support-strip">
            پاسخ خود را پیدا نکردید؟{' '}
            <Link className="button" to="/tickets/new">
              ثبت درخواست
            </Link>
          </div>
        </article>
      )}
    </RequestState>
  );
}

export function FAQPage() {
  const query = usePublic('faqs/');
  return (
    <>
      <PageHeader title="پرسش‌های متداول" />
      <RequestState query={query}>
        {(rows) =>
          rows.length ? (
            <div className="reading-page">
              {rows.map((f) => (
                <details className="faq-row" key={f.id}>
                  <summary>{f.question}</summary>
                  <div className="pre-wrap">{f.answer}</div>
                  {f.article && <Link to={'/knowledge/' + f.article}>راهنمای مرتبط ←</Link>}
                </details>
              ))}
            </div>
          ) : (
            <EmptyState title="پرسشی منتشر نشده است" />
          )
        }
      </RequestState>
    </>
  );
}

export function DepartmentsPage() {
  const { id } = useParams();
  const query = usePublic('departments/' + (id ? id + '/' : ''));
  return (
    <RequestState query={query}>
      {(data) =>
        id ? (
          <>
            <PageHeader title={data.department.name} />
            <p>{data.department.description}</p>
            <div className="support-strip">
              <span>{data.department.business_hours}</span>
              <span dir="ltr">{data.department.phone}</span>
              <a dir="ltr" href={'mailto:' + data.department.email}>
                {data.department.email}
              </a>
              <Link className="button" to={'/tickets/new?department=' + id}>
                ثبت درخواست برای این واحد
              </Link>
            </div>
            <h2>خدمات قابل درخواست</h2>
            <div className="department-grid">
              {data.categories.map((c) => (
                <span className="department-link" key={c.id}>
                  {c.name}
                </span>
              ))}
            </div>
            <h2>راهنماهای این واحد</h2>
            <ArticleCards articles={data.articles} />
          </>
        ) : (
          <>
            <PageHeader title="واحدهای پاسخگو" />
            <div className="content-grid">
              {data.map((d) => (
                <Link className="panel content-card" key={d.id} to={'/departments/' + d.id}>
                  <h2>{d.name}</h2>
                  <p>{d.description}</p>
                  <span>{d.business_hours}</span>
                </Link>
              ))}
            </div>
            {!data.length && <EmptyState title="واحدی برای نمایش وجود ندارد" />}
          </>
        )
      }
    </RequestState>
  );
}

function AnnouncementList({ rows }) {
  return rows.length ? (
    <div className="announcement-list">
      {rows.map((a) => (
        <Link className="announcement-row" to={'/announcements/' + a.id} key={a.id}>
          <strong>
            {a.pinned && '⌖ '}
            {a.title}
          </strong>
          <span>{date(a.starts_at)}</span>
        </Link>
      ))}
    </div>
  ) : (
    <EmptyState title="اطلاعیه فعالی وجود ندارد" />
  );
}

export function AnnouncementsPage() {
  const { id } = useParams();
  const query = usePublic('announcements/' + (id ? id + '/' : ''));
  return (
    <RequestState query={query}>
      {(data) =>
        id ? (
          <article className="reading-page">
            <PageHeader title={data.title} />
            <p>{date(data.starts_at)}</p>
            <div className="pre-wrap article-content">{data.content}</div>
          </article>
        ) : (
          <>
            <PageHeader title="اطلاعیه‌های دانشگاه" />
            <AnnouncementList rows={data} />
          </>
        )
      }
    </RequestState>
  );
}

const information = {
  about: [
    'درباره سامانه',
    'این سامانه برای راهنمایی، ثبت درخواست و پیگیری پاسخگویی دانشجویان دانشگاه صنعتی نوشیروانی بابل در حال توسعه است. واحدها، اطلاعات تماس و سیاست‌های نمایشی باید پیش از بهره‌برداری به تأیید دانشگاه برسند.',
  ],
  privacy: [
    'حریم خصوصی',
    'اطلاعات درخواست فقط برای صاحب درخواست و کارکنان دارای مجوز قابل مشاهده است. از ثبت رمز عبور، کد ملی و اطلاعات غیرضروری خودداری کنید. یادداشت‌های داخلی به دانشجو نمایش داده نمی‌شوند. سیاست نهایی نگهداری و حذف اطلاعات باید توسط دانشگاه تصویب شود.',
  ],
  accessibility: [
    'دسترس‌پذیری',
    'رابط برای استفاده با صفحه‌کلید، نمایش راست‌به‌چپ و اندازه‌های مختلف صفحه طراحی شده است. ارزیابی کامل انطباق دسترس‌پذیری هنوز انجام نشده است. در صورت مشکل، از مسیر درخواست پشتیبانی اطلاع دهید.',
  ],
};
export function InformationPage({ kind }) {
  const [title, text] = information[kind];
  return (
    <article className="reading-page">
      <PageHeader title={title} />
      <p className="article-content">{text}</p>
    </article>
  );
}
