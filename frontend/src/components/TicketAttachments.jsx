import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { Alert, Field } from './ui';

export default function TicketAttachments({ ticket }) {
  const client = useQueryClient();
  const [file, setFile] = useState(null);
  const mutation = useMutation({
    mutationFn: () => {
      const body = new FormData();
      body.append('file', file);
      return api('/tickets/' + ticket.id + '/attachments/', { method: 'POST', body });
    },
    onSuccess: () => client.invalidateQueries({ queryKey: ['ticket', String(ticket.id)] }),
  });
  return (
    <section className="panel panel-pad">
      <h2>مدارک پیوست</h2>
      {ticket.attachments.map((a) => (
        <div className="ticket-row" key={a.id}>
          <a href={'/api/v1/tickets/' + ticket.id + '/attachments/' + a.id + '/'}>
            {a.original_name}
          </a>
          <small>{Math.ceil(a.size / 1024)} کیلوبایت</small>
        </div>
      ))}
      {!['resolved', 'closed'].includes(ticket.status) &&
        ticket.allowed_actions.permissions.includes('reply') && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              mutation.mutate();
            }}
          >
            <Alert>{mutation.error?.message}</Alert>
            <Field
              label="افزودن مدرک"
              name="attachment"
              hint="PDF، PNG، JPG یا WebP؛ حداکثر ۱۰ مگابایت. رمز عبور و اطلاعات غیرضروری ارسال نکنید."
            >
              <input
                id="attachment"
                type="file"
                required
                accept=".pdf,.png,.jpg,.jpeg,.webp"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </Field>
            <button disabled={mutation.isPending}>
              {mutation.isPending ? 'در حال بارگذاری…' : 'بارگذاری مدرک'}
            </button>
          </form>
        )}
    </section>
  );
}
