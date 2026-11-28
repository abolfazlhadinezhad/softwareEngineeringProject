import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { expect, it, vi } from 'vitest';
import LoginPage from './LoginPage';
import { useAuth } from '../features/auth/AuthProvider';
vi.mock('../features/auth/AuthProvider', () => ({ useAuth: vi.fn() }));

it('uses labeled required fields and submits credentials', async () => {
  const signIn = vi.fn().mockResolvedValue({ id: 1 });
  useAuth.mockReturnValue({ user: null, isLoading: false, signIn });
  render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
  expect(screen.getByLabelText('شماره دانشجویی')).toBeRequired();
  expect(screen.getByLabelText('رمز عبور')).toHaveAttribute('type', 'password');
  await userEvent.type(screen.getByLabelText('شماره دانشجویی'), 'student');
  await userEvent.type(screen.getByLabelText('رمز عبور'), 'password');
  await userEvent.click(screen.getByRole('button', { name: /ورود به سامانه/ }));
  expect(signIn).toHaveBeenCalledWith({
    username: 'student',
    password: 'password',
    portal: 'student',
  });
});
it('shows credential errors and restores submit action', async () => {
  useAuth.mockReturnValue({
    user: null,
    isLoading: false,
    signIn: vi.fn().mockRejectedValue(new Error('Invalid credentials.')),
  });
  render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
  await userEvent.type(screen.getByLabelText('شماره دانشجویی'), 'x');
  await userEvent.type(screen.getByLabelText('رمز عبور'), 'x');
  await userEvent.click(screen.getByRole('button', { name: /ورود به سامانه/ }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Invalid credentials.');
  expect(screen.getByRole('button', { name: /ورود به سامانه/ })).toBeEnabled();
});
