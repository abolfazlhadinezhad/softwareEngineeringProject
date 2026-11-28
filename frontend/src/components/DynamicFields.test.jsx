import { render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import DynamicFields from './DynamicFields';

it('shows required conditional fields only for the matching answer', () => {
  const fields = [
    { key: 'kind', type: 'select', label: 'خدمت', required: true, options: ['شبکه', 'حساب'] },
    {
      key: 'device',
      type: 'text',
      label: 'دستگاه',
      required: true,
      visible_when: { field: 'kind', equals: 'شبکه' },
    },
  ];
  const { rerender } = render(
    <DynamicFields fields={fields} value={{ kind: 'حساب' }} onChange={vi.fn()} />,
  );
  expect(screen.getByLabelText('خدمت')).toBeRequired();
  expect(screen.queryByLabelText('دستگاه')).not.toBeInTheDocument();
  rerender(<DynamicFields fields={fields} value={{ kind: 'شبکه' }} onChange={vi.fn()} />);
  expect(screen.getByLabelText('دستگاه')).toBeRequired();
});
