import React from 'react';
import '../styles/Input.css';

export default function Input({ label, error, hint, id, ...props }) {
  return (
    <div className="input-wrapper">
      {label && <label htmlFor={id} className="input-label">{label}</label>}
      <input
        id={id}
        className={`input ${error ? 'input-error' : ''}`}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        {...props}
      />
      {error && <span id={`${id}-error`} className="input-error-text" role="alert">{error}</span>}
      {hint && !error && <span id={`${id}-hint`} className="input-hint">{hint}</span>}
    </div>
  );
}

export function Textarea({ label, error, hint, id, ...props }) {
  return (
    <div className="input-wrapper">
      {label && <label htmlFor={id} className="input-label">{label}</label>}
      <textarea
        id={id}
        className={`input textarea ${error ? 'input-error' : ''}`}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        {...props}
      />
      {error && <span id={`${id}-error`} className="input-error-text" role="alert">{error}</span>}
      {hint && !error && <span id={`${id}-hint`} className="input-hint">{hint}</span>}
    </div>
  );
}

export function Select({ label, error, hint, id, options, ...props }) {
  return (
    <div className="input-wrapper">
      {label && <label htmlFor={id} className="input-label">{label}</label>}
      <select
        id={id}
        className={`input select ${error ? 'input-error' : ''}`}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
      {error && <span id={`${id}-error`} className="input-error-text" role="alert">{error}</span>}
      {hint && !error && <span id={`${id}-hint`} className="input-hint">{hint}</span>}
    </div>
  );
}