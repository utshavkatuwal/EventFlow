import React from 'react';
import '../styles/Button.css';

export function Button({ variant = 'primary', size = 'md', children, onClick, disabled, type = 'button' }) {
  return (
    <button
      type={type}
      className={`btn btn-${variant} btn-${size}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
