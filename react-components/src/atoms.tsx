import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export function Button({ variant = 'primary', loading = false, children, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant; loading?: boolean }) {
  return <button {...props} className={`u-button u-button-${variant} ${props.className ?? ''}`} aria-busy={loading}>{loading && <span className="u-spinner" aria-hidden="true" />}{children}</button>;
}

export function Input({ className = '', ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`u-input ${className}`} />;
}

export function Logo({ href = '/', compact = false }: { href?: string; compact?: boolean }) {
  return <a className={`u-logo ${compact ? 'u-logo-compact' : ''}`} href={href} aria-label="UniLaunch"><span className="u-logo-mark">U</span>{!compact && <span>UniLaunch</span>}</a>;
}

export function Badge({ text, tone = 'neutral' }: { text: string; tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'accent' }) {
  return <span className={`u-badge u-badge-${tone}`}>{text}</span>;
}

export function Avatar({ name, src, size = 'medium' }: { name: string; src?: string; size?: 'small' | 'medium' | 'large' }) {
  const initials = name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
  return src ? <img className={`u-avatar u-avatar-${size}`} src={src} alt={name} /> : <span className={`u-avatar u-avatar-${size}`} aria-label={name}>{initials}</span>;
}

export function ProgressBar({ value = 0, label = '', color = '#56806f' }: { value?: number; label?: string; color?: string }) {
  const safeValue = Math.max(0, Math.min(100, value));
  return <div className="u-progress" role="progressbar" aria-label={label || undefined} aria-valuemin={0} aria-valuemax={100} aria-valuenow={safeValue}><span style={{ width: `${safeValue}%`, backgroundColor: color }} /></div>;
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <section className={`u-card ${className}`}>{children}</section>;
}
