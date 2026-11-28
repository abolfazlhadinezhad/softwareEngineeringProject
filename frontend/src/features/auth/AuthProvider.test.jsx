import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { AuthProvider, useAuth } from './AuthProvider';

function SessionProbe() {
  const { user, signIn, signOut } = useAuth();
  return (
    <main>
      <p>{user ? `${user.username}:${user.role}` : 'signed out'}</p>
      <button onClick={() => signIn({ username: 'student', password: 'test' })}>Sign in</button>
      <button onClick={() => signOut()}>Sign out</button>
    </main>
  );
}

afterEach(() => vi.unstubAllGlobals());

it('updates the observed session on login and logout while clearing other user data', async () => {
  const csrf = { ok: true, json: async () => ({ csrfToken: 'csrf-test' }) };
  const denied = {
    ok: false,
    status: 403,
    json: async () => ({ error: { details: { detail: 'Sign in required.' } } }),
  };
  const authenticated = {
    ok: true,
    status: 200,
    json: async () => ({ id: 4, username: 'student', role: 'student' }),
  };
  const loggedOut = { ok: true, status: 204 };
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(denied)
    .mockResolvedValueOnce(csrf)
    .mockResolvedValueOnce(authenticated)
    .mockResolvedValueOnce(csrf)
    .mockResolvedValueOnce(loggedOut);
  vi.stubGlobal('fetch', fetch);

  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  client.setQueryData(['tickets', 'previous-account'], [{ id: 100 }]);
  render(
    <QueryClientProvider client={client}>
      <AuthProvider>
        <SessionProbe />
      </AuthProvider>
    </QueryClientProvider>,
  );
  await screen.findByText('signed out');
  fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  await screen.findByText('student:student');
  expect(client.getQueryData(['tickets', 'previous-account'])).toBeUndefined();
  fireEvent.click(screen.getByRole('button', { name: 'Sign out' }));
  await waitFor(() => expect(screen.getByText('signed out')).toBeVisible());
  expect(client.getQueryData(['tickets', 'previous-account'])).toBeUndefined();
});
