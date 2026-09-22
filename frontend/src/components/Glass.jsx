import React from 'react';

/* One design language — every surface uses the same glass tokens.
   Use these instead of hand-rolled divs so all UI stays consistent. */
export function GlassCard({ children, className = '', ...rest }) {
  return <div className={`glass-secondary ${className}`} {...rest}>{children}</div>;
}
export function GlassPanel({ children, className = '', ...rest }) {
  return <div className={`glass-primary glass-stroke ${className}`} {...rest}>{children}</div>;
}
export function GlassBadge({ children, className = '', ...rest }) {
  return <span className={`glass-tert ${className}`} {...rest}>{children}</span>;
}
export function GlassChip({ children, active, className = '', ...rest }) {
  return <button className={`dchip ${active ? 'on' : ''} ${className}`} {...rest}>{children}</button>;
}
export function GlassButton({ children, variant = 'primary', size = 'md', className = '', ...rest }) {
  return <button className={`btn btn-${variant} btn-${size} ${className}`} {...rest}>{children}</button>;
}
export function GlassInput(props) {
  return <input className="input-field" {...props} />;
}
