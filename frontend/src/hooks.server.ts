import { redirect } from '@sveltejs/kit';
import type { Handle } from '@sveltejs/kit';
import { backendFetch } from '$lib/server/backend';
import type { User } from './app';

export const handle: Handle = async ({ event, resolve }) => {
	const pathname = event.url.pathname;
	const isStaticAsset =
		pathname.startsWith('/_app/') ||
		pathname === '/favicon.svg' ||
		pathname === '/robots.txt' ||
		pathname === '/service-worker.js' ||
		/\.(?:css|js|map|png|jpe?g|gif|webp|svg|ico|woff2?)$/i.test(pathname);

	if (isStaticAsset) {
		return resolve(event);
	}

	const sessionToken = event.cookies.get('session_token');
	let sessionIsInvalid = false;

	if (sessionToken) {
		try {
			const response = await backendFetch('/api/v1/usuarios/me', sessionToken);
			if (response.ok) {
				const user = (await response.json()) as User;
				if (user && user.id) {
					event.locals.user = user;
					event.locals.userId = user.id;
					event.locals.token = sessionToken;
				} else {
					sessionIsInvalid = true;
				}
			} else {
				sessionIsInvalid = true;
			}
		} catch {
			// Erros transitórios de rede não quebram o hook imediatamente
		}
	}

	if (sessionIsInvalid) {
		event.cookies.delete('session_token', { path: '/' });
		event.locals.user = null;
		event.locals.userId = undefined;
		event.locals.token = undefined;
	}

	const isApiRoute = pathname.startsWith('/api/');
	const isPublicPage = ['/login', '/cadastro', '/recuperar-senha', '/reset-password', '/playground'].some(
		(path) => pathname === path || pathname.startsWith(`${path}/`)
	);

	if (!event.locals.user && !isApiRoute && !isPublicPage) {
		const next = `${pathname}${event.url.search}`;
		throw redirect(303, `/login?next=${encodeURIComponent(next)}`);
	}

	const response = await resolve(event);

	// Injeção de cabeçalhos de segurança (OWASP Security Headers)
	response.headers.set('X-Frame-Options', 'DENY');
	response.headers.set('X-Content-Type-Options', 'nosniff');
	response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
	response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
	response.headers.set('Cross-Origin-Opener-Policy', 'same-origin');

	if (!import.meta.env.DEV) {
		response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
	}

	return response;
};
