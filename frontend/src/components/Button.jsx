import React from 'react';
import { Link } from 'react-router-dom';
import { useApi } from '../context/ApiContext';
import './Button.css';

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
