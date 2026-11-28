import { expect, test } from '@playwright/test';

const password = process.env.E2E_TEST_PASSWORD;

async function signIn(page, username) {
  await page.goto('/login');
  await expect(page.getByRole('heading', { name: 'Welcome back.' })).toBeVisible();
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/tickets$/);
}

test('students submit private tickets and support staff resolve a conversation', async ({ page }) => {
  test.skip(!password, 'Set E2E_TEST_PASSWORD to run the disposable development-account browser workflow.');
  const title = `Portal access ${Date.now()}`;

  await signIn(page, 'e2e_student');
  await page.getByRole('link', { name: /new ticket/i }).click();
  await expect(page).toHaveURL(/\/tickets\/new$/);
  await page.getByLabel('Title', { exact: true }).fill(title);
  await page.getByLabel('Category').selectOption({ label: 'Browser test support' });
  await page.getByLabel('Priority').selectOption('high');
  await page.getByLabel('Description').fill('I cannot access the student portal after signing in.');
  await page.getByRole('button', { name: /submit ticket/i }).click();
  await expect(page.getByRole('heading', { name: title })).toBeVisible();
  await expect(page.getByText('I cannot access the student portal after signing in.')).toBeVisible();
  await expect(page.getByText('Open', { exact: true }).first()).toBeVisible();

  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page).toHaveURL(/\/login$/);
  await signIn(page, 'e2e_support');
  await page.getByRole('link', { name: new RegExp(title) }).click();
  await expect(page.getByRole('heading', { name: title })).toBeVisible();
  await page.getByRole('button', { name: 'Claim ticket' }).click();
  await expect(page.getByLabel('Change status')).toHaveValue('in_progress');
  await page.getByLabel('Reply', { exact: true }).fill('We are checking your portal access now.');
  await page.getByRole('button', { name: /send reply/i }).click();
  await expect(page.getByText('We are checking your portal access now.')).toBeVisible();
  await page.getByLabel('Change status').selectOption('waiting_student');
  await expect(page.getByLabel('Change status')).toHaveValue('waiting_student');

  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page).toHaveURL(/\/login$/);
  await signIn(page, 'e2e_other_student');
  await expect(page.getByRole('link', { name: new RegExp(title) })).toHaveCount(0);
});

test('the sign-in flow fits a narrow mobile viewport', async ({ page }) => {
  test.skip(!password, 'Set E2E_TEST_PASSWORD to run the disposable development-account browser workflow.');
  await page.setViewportSize({ width: 390, height: 844 });
  await signIn(page, 'e2e_student');
  const sizes = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, document: document.documentElement.scrollWidth }));
  expect(sizes.document).toBeLessThanOrEqual(sizes.viewport);
  await expect(page.getByRole('heading', { name: 'Your tickets.' })).toBeVisible();
});
