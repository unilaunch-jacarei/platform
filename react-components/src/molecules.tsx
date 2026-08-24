import { useState } from 'react';
import type { ChangeEvent, InputHTMLAttributes, ReactNode } from 'react';
import { Badge, Card, Input, ProgressBar } from './atoms';

export function FormField({ id, label, error, onChange, ...props }: InputHTMLAttributes<HTMLInputElement> & { id: string; label: string; error?: string; onChange?: (event: ChangeEvent<HTMLInputElement>) => void }) {
  const errorId = error ? `${id}-error` : undefined;
  return <div className="u-field"><label htmlFor={id}>{label}</label><Input {...props} id={id} onChange={onChange} aria-invalid={Boolean(error)} aria-describedby={errorId} />{error && <p id={errorId} className="u-error" role="alert">{error}</p>}</div>;
}

export function PasswordField({ label = 'Senha', value, onChange, ...props }: Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> & { label?: string }) {
  const [visible, setVisible] = useState(false);
  return <div className="u-password"><FormField {...props} label={label} type={visible ? 'text' : 'password'} value={value} onChange={onChange} /><button type="button" className="u-password-toggle" onClick={() => setVisible((current) => !current)} aria-pressed={visible}>{visible ? 'Ocultar' : 'Mostrar'}</button></div>;
}

export function PasswordCriteria({ value }: { value: string }) {
  const checks = [{ label: 'Minimo de 8 caracteres', valid: value.length >= 8 }, { label: 'Uma letra maiuscula', valid: /[A-Z]/.test(value) }, { label: 'Um numero', valid: /\d/.test(value) }];
  return <ul className="u-criteria" aria-label="Requisitos da senha">{checks.map((check) => <li className={check.valid ? 'is-valid' : ''} key={check.label}><span aria-hidden="true">{check.valid ? 'OK' : '○'}</span>{check.label}</li>)}</ul>;
}

export function SearchField({ value, onChange, placeholder = 'Buscar...', ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <div className="u-search"><span aria-hidden="true">⌕</span><Input {...props} value={value} onChange={onChange} placeholder={placeholder} aria-label={placeholder} /></div>;
}

export function StatCard({ label, value, detail, icon }: { label: string; value: string | number; detail?: string; icon?: ReactNode }) {
  return <Card className="u-stat"><span className="u-stat-icon" aria-hidden="true">{icon}</span><div><p>{label}</p><strong>{value}</strong>{detail && <small>{detail}</small>}</div></Card>;
}

export function ProjectCard({ name, description, team, progress = 0, status = 'Em andamento', technologies = [], onOpen }: { name: string; description: string; team?: string; progress?: number; status?: string; technologies?: string[]; onOpen: () => void }) {
  const tone = status === 'Finalizado' ? 'success' : status === 'Atenção' ? 'warning' : status === 'Pausado' ? 'neutral' : 'accent';
  return <Card><article className="u-project"><div className="u-project-heading"><div><h3>{name}</h3>{team && <p>{team}</p>}</div><Badge text={status} tone={tone} /></div><p>{description}</p><div className="u-tags">{technologies.slice(0, 4).map((technology) => <span key={technology}>{technology}</span>)}</div><div className="u-progress-label"><span>Progresso</span><strong>{progress}%</strong></div><ProgressBar value={progress} /><button className="u-link-button" type="button" onClick={onOpen}>Abrir projeto <span aria-hidden="true">→</span></button></article></Card>;
}
