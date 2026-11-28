import { Field } from './ui';

export default function DynamicFields({ fields = [], value, onChange }) {
  return fields
    .filter((f) => !f.visible_when || value[f.visible_when.field] === f.visible_when.equals)
    .map((f) => {
      const id = 'custom-' + f.key;
      const props = {
        id,
        required: f.required,
        value: value[f.key] ?? '',
        onChange: (e) => onChange({ ...value, [f.key]: e.target.value }),
      };
      let input;
      if (f.type === 'textarea') input = <textarea {...props} maxLength={f.max_length || 5000} />;
      else if (['select', 'radio'].includes(f.type))
        input = (
          <select {...props}>
            <option value="">انتخاب کنید</option>
            {f.options.map((o) => (
              <option key={o}>{o}</option>
            ))}
          </select>
        );
      else if (f.type === 'checkbox')
        input = (
          <input
            id={id}
            type="checkbox"
            checked={!!value[f.key]}
            onChange={(e) => onChange({ ...value, [f.key]: e.target.checked })}
          />
        );
      else if (f.type === 'multiselect')
        input = (
          <select
            {...props}
            multiple
            value={value[f.key] || []}
            onChange={(e) =>
              onChange({ ...value, [f.key]: [...e.target.selectedOptions].map((o) => o.value) })
            }
          >
            {f.options.map((o) => (
              <option key={o}>{o}</option>
            ))}
          </select>
        );
      else
        input = (
          <input
            {...props}
            type={['number', 'date', 'time'].includes(f.type) ? f.type : 'text'}
            min={f.min}
            max={f.max}
            maxLength={f.max_length || 5000}
            onChange={(e) =>
              onChange({
                ...value,
                [f.key]:
                  f.type === 'number' && e.target.value !== ''
                    ? Number(e.target.value)
                    : e.target.value,
              })
            }
          />
        );
      return (
        <Field key={f.key} label={f.label} name={id} hint={f.help_text}>
          {input}
        </Field>
      );
    });
}
