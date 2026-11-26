export class ApiError extends Error {
  constructor(status, details) {
    const messages = (value) => typeof value === 'string' ? [value] : Object.values(value || {}).flatMap(messages);
    super(messages(details).join(' ') || 'The request could not be completed.');
    this.status = status;
    this.details = details;
  }
}

export async function api(path, options = {}) {
  const method = options.method || 'GET';
  const headers = { Accept: 'application/json', ...options.headers };
  if (!['GET', 'HEAD'].includes(method)) {
    const csrf = await fetch('/api/auth/csrf/', { credentials: 'same-origin', cache: 'no-store' });
    if (!csrf.ok) throw new ApiError(csrf.status, { detail: 'Unable to establish a secure session. Please retry.' });
    headers['X-CSRFToken'] = (await csrf.json()).csrfToken;
    headers['Content-Type'] = 'application/json';
  }
  const response = await fetch(`/api${path}`, { ...options, method, headers, credentials: 'same-origin', cache: 'no-store', body: options.body === undefined ? undefined : JSON.stringify(options.body) });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({ error: { details: { detail: 'The server returned an unexpected response.' } } }));
  if (!response.ok) throw new ApiError(response.status, data.error?.details || data);
  return data;
}
