import { expect, test } from '@playwright/test';

const password = process.env.E2E_TEST_PASSWORD;

async function signIn(page, username, portal = 'student') {
  await page.goto(
    portal === 'student' ? '/login' : portal === 'admin' ? '/control/login' : '/staff/login',
  );
  await page.getByLabel(portal === 'student' ? 'شماره دانشجویی' : 'نام کاربری').fill(username);
  await page.getByLabel('رمز عبور', { exact: true }).fill(password);
  await page.getByRole('button', { name: /ورود به سامانه/ }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test('guest finds Persian help without a session on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /پرسش شما/ })).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await page.getByLabel('جستجو در راهنما').fill('اينترنت');
  await page.getByRole('button', { name: 'جستجو', exact: true }).click();
  await page.getByRole('heading', { name: 'راهنمای اتصال به اینترنت دانشگاه (نمایشی)' }).click();
  await expect(
    page.getByText('ابتدا اتصال شبکه دستگاه خود را بررسی کنید.', { exact: false }),
  ).toBeVisible();
  await page.goto('/faq');
  await page.getByText('چگونه وضعیت درخواست خود را پیگیری کنم؟', { exact: true }).click();
  await expect(page.getByText(/بخش درخواست‌های من را باز کنید/)).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= document.documentElement.clientWidth,
    ),
  ).toBe(true);
});

test('student and scoped employee complete a private support conversation', async ({
  page,
  browser,
}) => {
  test.skip(!password, 'Set E2E_TEST_PASSWORD for synthetic development accounts.');
  const title = 'درخواست آزمایشی ' + Date.now();
  await signIn(page, 'e2e_student');
  await page
    .getByRole('link', { name: /درخواست جدید/ })
    .first()
    .click();
  await page.getByLabel('موضوع درخواست').fill(title);
  await page.getByRole('button', { name: 'ادامه ←' }).click();
  await page.getByRole('button', { name: 'ادامه ←' }).click();
  await page
    .getByLabel('واحد مسئول', { exact: true })
    .selectOption({ label: 'فناوری اطلاعات (آزمایشی)' });
  await page
    .getByLabel('دسته‌بندی', { exact: true })
    .selectOption({ label: 'Browser test support' });
  await page.getByLabel('خدمت مورد نظر').selectOption('اینترنت');
  await page.getByLabel('شرح درخواست').fill('درخواست ساختگی برای بررسی اتصال پرتال و ثبت نتیجه.');
  await page.getByRole('button', { name: 'ادامه ←' }).click();
  await page.getByRole('button', { name: 'ثبت نهایی درخواست' }).click();
  await expect(page.getByRole('heading', { name: title, exact: true })).toBeVisible();
  const ticketUrl = page.url();
  const ticketId = ticketUrl.split('/').pop();
  await page
    .getByLabel('افزودن مدرک')
    .setInputFiles({
      name: 'synthetic.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('%PDF-1.7\nSynthetic development document'),
    });
  await page.getByRole('button', { name: 'بارگذاری مدرک' }).click();
  await expect(page.getByRole('link', { name: 'synthetic.pdf' })).toBeVisible();

  const staffContext = await browser.newContext();
  const staff = await staffContext.newPage();
  await signIn(staff, 'e2e_support', 'staff');
  await staff.goto('/tickets/' + ticketId);
  await staff.getByRole('button', { name: 'دریافت درخواست', exact: true }).click();
  await staff.getByLabel('یادداشت داخلی', { exact: true }).fill('INTERNAL-PRIVATE-ONLY');
  await staff.getByRole('button', { name: 'ذخیره یادداشت داخلی' }).click();
  await expect(staff.getByText('INTERNAL-PRIVATE-ONLY', { exact: true })).toBeVisible();
  await staff.getByLabel('پاسخ', { exact: true }).fill('پاسخ رسمی کارشناس برای بررسی اتصال.');
  await staff.getByRole('button', { name: 'ارسال پاسخ', exact: true }).click();
  await expect(page.getByText('پاسخ رسمی کارشناس برای بررسی اتصال.', { exact: true })).toBeVisible({
    timeout: 22000,
  });
  await expect(page.getByText('INTERNAL-PRIVATE-ONLY')).toHaveCount(0);
  await page.getByLabel('پاسخ', { exact: true }).fill('اطلاعات تکمیلی دانشجو دریافت شد.');
  await page.getByRole('button', { name: 'ارسال پاسخ', exact: true }).click();
  await expect(staff.getByText('اطلاعات تکمیلی دانشجو دریافت شد.', { exact: true })).toBeVisible({
    timeout: 22000,
  });
  await staff.getByLabel('دلیل عملیات / نتیجه رسیدگی').fill('اتصال بررسی و مشکل آزمایشی رفع شد.');
  await staff.getByRole('button', { name: 'حل‌شده', exact: true }).click();
  await expect(page.getByRole('button', { name: 'تأیید حل مسئله' })).toBeVisible({
    timeout: 22000,
  });
  await page.getByRole('button', { name: 'تأیید حل مسئله' }).click();
  await page.getByRole('button', { name: 'ثبت ارزیابی' }).click();
  await expect(page.getByText('ارزیابی ثبت شد.', { exact: true })).toBeVisible();

  const otherContext = await browser.newContext();
  const other = await otherContext.newPage();
  await signIn(other, 'e2e_other_student');
  await other.goto('/tickets/' + ticketId);
  await expect(other.getByRole('heading', { name: title })).toHaveCount(0);
  await expect(other.getByRole('alert')).toBeVisible();
  const unauthorizedFile = await other.request.get(
    '/api/v1/tickets/' +
      ticketId +
      '/attachments/' +
      (await page.locator('a[href*="/attachments/"]').getAttribute('href'))
        .split('/')
        .filter(Boolean)
        .pop() +
      '/',
  );
  expect(unauthorizedFile.status()).toBe(404);
  await otherContext.close();
  await staffContext.close();
});

test('administrator configures a department and category using React forms', async ({ page }) => {
  test.skip(!password, 'Set E2E_TEST_PASSWORD for synthetic development accounts.');
  const suffix = Date.now();
  await signIn(page, 'e2e_admin', 'admin');
  await page.goto('/manage/departments');
  await page.getByLabel('نام', { exact: true }).fill('واحد نمایشی ' + suffix);
  await page.getByLabel('شناسه یکتا', { exact: true }).fill('demo-' + suffix);
  await page.getByRole('button', { name: 'ذخیره', exact: true }).click();
  await expect(page.getByText('اطلاعات ذخیره شد.', { exact: true })).toBeVisible();
  const response = await page.request.get('/api/v1/manage/departments/');
  const departments = await response.json();
  const department = departments.results.find((d) => d.slug === 'demo-' + suffix);
  await page.goto('/manage/categories');
  await page.getByLabel('نام', { exact: true }).fill('دسته نمایشی ' + suffix);
  await page.getByLabel('شناسه واحد', { exact: true }).fill(String(department.id));
  await page.getByRole('button', { name: 'ذخیره', exact: true }).click();
  await expect(page.getByText('اطلاعات ذخیره شد.', { exact: true })).toBeVisible();
});

test('department manager sees recorded operational metrics', async ({ page }) => {
  test.skip(!password, 'Set E2E_TEST_PASSWORD for synthetic development accounts.');
  await signIn(page, 'e2e_manager', 'staff');
  await expect(page.getByRole('heading', { name: 'کیفیت پاسخگویی' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'بار کاری کارشناسان' })).toBeVisible();
});
