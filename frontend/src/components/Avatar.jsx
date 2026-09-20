import React from 'react';
import './Avatar.css';

export default function Avatar({ name, size = 'md', className = '' }) {
  const initials = name
    ?.split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || '?';

  const sizeClasses = {
    xs: 'avatar-xs',
    sm: 'avatar-sm',
    md: 'avatar-md',
    lg: 'avatar-lg',
    xl: 'avatar-xl',
  };

  return (
    <div className={`avatar ${sizeClasses[size]} ${className}`} aria-label={name}>
      {initials}
    </div>
  );
}