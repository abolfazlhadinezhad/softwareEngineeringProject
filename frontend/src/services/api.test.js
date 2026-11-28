import { afterEach, expect, it, vi } from 'vitest';
import { api, ApiError } from './api';

afterEach(() => vi.unstubAllGlobals());
it('bootstraps CSRF and submits JSON using same-origin credentials', async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce({ ok: true, json: async () => ({ csrfToken: 'test-token' }) })
    .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ id: 1 }) });
  vi.stubGlobal('fetch', fetch);
  await expect(
    api('/auth/login/', { method: 'POST', body: { username: 'student', password: 'test' } }),
  ).resolves.toEqual({ id: 1 });
  expect(fetch.mock.calls[1][1]).toMatchObject({
    credentials: 'same-origin',
    headers: { 'X-CSRFToken': 'test-token', 'Content-Type': 'application/json' },
  });
});
it('exposes structured validation errors', async () => {
  vi.stubGlobal(
    'fetch',
    vi
      .fn()
      .mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({ error: { details: { detail: 'Permission denied.' } } }),
      }),
  );
  await expect(api('/auth/me/')).rejects.toMatchObject({
    status: 403,
    message: 'Permission denied.',
  });
});
it('handles empty successful responses without parsing JSON', async () => {
  vi.stubGlobal(
    'fetch',
    vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ csrfToken: 't' }) })
      .mockResolvedValueOnce({ ok: true, status: 204 }),
  );
  await expect(api('/auth/logout/', { method: 'POST' })).resolves.toBeNull();
});
it('formats nested field errors', () => {
  expect(new ApiError(400, { title: ['Required.'] }).message).toBe('Required.');
});
