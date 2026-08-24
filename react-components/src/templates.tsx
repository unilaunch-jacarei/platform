import type { ReactNode } from 'react';
import { AuthBrandPanel } from './organisms';

export function AuthLayout({ eyebrow, title, children }: { eyebrow: string; title: string; children: ReactNode }) { return <div className="u-auth-layout"><AuthBrandPanel /><main><div className="u-auth-content"><p className="u-eyebrow">{eyebrow}</p><h2>{title}</h2>{children}</div></main></div>; }
