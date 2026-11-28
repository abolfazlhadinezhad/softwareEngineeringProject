import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../features/auth/AuthProvider';
import { api } from '../services/api';
import { Badge, EmptyState, ErrorState, Loading, PageHeader, date } from '../components/ui';

export default function PortalDashboard() {
  const { user } = useAuth();
  const query = useQuery({
    queryKey: ['dashboard'],
    queryFn: ({ signal }) => api('/dashboard/', { signal }),
    refetchInterval: 30000,
  });
  if (query.isPending) return <Loading />;
  if (query.error) return <ErrorState error={query.error} retry={query.refetch} />;
  const d = query.data;
  const student = user.role === 'student';
  const manager = user.capabilities?.includes('report.view.department');
  return (
    <>
      <PageHeader
        eyebrow={
          student
            ? 'پیشخوان دانشجو'
            : d.university
              ? 'مدیریت سامانه'
              : manager
                ? 'مدیریت واحد'
                : 'میز خدمت کارکنان'
        }
        title={'سلام، ' + (user.first_name || user.username)}
        action={
          student && (
            <Link className="button" to="/tickets/new">
              ＋ درخواست جدید
            </Link>
          )
        }
      >
        {student
          ? 'پاسخ‌ها و درخواست‌های نیازمند توجه شما در یک نگاه.'
          : 'صف‌های رسیدگی و عملکرد ثبت‌شده را بررسی کنید.'}
      </PageHeader>
      <div className="stats">
        {(student
          ? [
              ['درخواست‌های من', d.total],
              ['منتظر پاسخ شما', d.counts.waiting_student || 0],
              ['حل‌شده', d.counts.resolved || 0],
            ]
          : [
              ['درخواست‌های قابل دسترسی', d.total],
              ['بدون مسئول', d.unassigned],
              ['گذشته از مهلت', d.overdue],
            ]
        ).map(([label, value]) => (
          <div className="panel stat" key={label}>
            <div>
              <span className="stat-label">{label}</span>
              <strong>{value.toLocaleString('fa-IR')}</strong>
            </div>
          </div>
        ))}
      </div>
      {d.university && (
        <section className="panel panel-pad">
          <h2>نمای کلی دانشگاه</h2>
          <div className="metrics-grid">
            {[
              ['دانشجو', d.university.students],
              ['دانشجوی فعال', d.university.active_students],
              ['کارمند', d.university.employees],
              ['واحد فعال', d.university.departments],
              ['کل درخواست‌ها', d.university.tickets],
            ].map(([k, v]) => (
              <div key={k}>
                <strong>{v.toLocaleString('fa-IR')}</strong>
                <span>{k}</span>
              </div>
            ))}
          </div>
          <Link to="/manage/departments">مدیریت ساختار سازمانی ←</Link>
        </section>
      )}
      {!student && (
        <section className="panel panel-pad">
          <h2>صف رسیدگی من</h2>
          <TicketRows rows={d.my_queue} />
        </section>
      )}
      <section className="panel panel-pad">
        <h2>{student ? 'آخرین درخواست‌ها و پاسخ‌ها' : 'آخرین فعالیت صف'}</h2>
        <TicketRows rows={d.recent} />
        <Link to="/tickets">مشاهده همه درخواست‌ها ←</Link>
      </section>
      {d.performance && (
        <div className="content-grid">
          <section className="panel panel-pad">
            <h2>کیفیت پاسخگویی</h2>
            <p>
              میانه اولین پاسخ:{' '}
              {d.performance.first_response_median_minutes == null
                ? 'داده کافی نیست'
                : Math.round(d.performance.first_response_median_minutes).toLocaleString('fa-IR') +
                  ' دقیقه'}
            </p>
            <p>
              میانه حل درخواست:{' '}
              {d.performance.resolution_median_minutes == null
                ? 'داده کافی نیست'
                : Math.round(d.performance.resolution_median_minutes).toLocaleString('fa-IR') +
                  ' دقیقه'}
            </p>
            <p>
              رضایت:{' '}
              {d.satisfaction.average == null
                ? 'هنوز ارزیابی ثبت نشده است'
                : d.satisfaction.average.toFixed(1) + ' از ۵'}{' '}
              · {d.satisfaction.responses} پاسخ
            </p>
          </section>
          <section className="panel panel-pad">
            <h2>حجم کار واحدها</h2>
            {d.by_department.map((r, i) => (
              <div className="report-row" key={i}>
                <span>{r.department__name || 'تعیین نشده'}</span>
                <strong>{r.count}</strong>
              </div>
            ))}
          </section>
          <section className="panel panel-pad">
            <h2>بار کاری کارشناسان</h2>
            {d.workload.map((r, i) => (
              <div className="report-row" key={i}>
                <span>{r.assignee__username || 'بدون مسئول'}</span>
                <strong>{r.count}</strong>
              </div>
            ))}
          </section>
        </div>
      )}
    </>
  );
}

function TicketRows({ rows = [] }) {
  return rows.length ? (
    <div>
      {rows.map((t) => (
        <Link className="ticket-row" key={t.id} to={'/tickets/' + t.id}>
          <div>
            <strong>{t.title}</strong>
            <small>{date(t.updated_at)}</small>
          </div>
          <Badge value={t.status} />
        </Link>
      ))}
    </div>
  ) : (
    <EmptyState title="درخواستی در این صف نیست" />
  );
}
