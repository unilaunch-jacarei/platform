import { redirect } from '@sveltejs/kit';
import type { Handle } from '@sveltejs/kit';
import { backendFetch } from '$lib/server/backend';

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

	const sessionId = event.cookies.get('session_id');
	let sessionIsInvalid = false;
	if (sessionId) {
		try {
			const response = await backendFetch('/api/v1/auth/session', sessionId, { method: 'POST' });
			if (response.ok) {
				const rawBody = await response.text();
				try {
					const body = JSON.parse(rawBody) as { user_id?: unknown };
					if (body.user_id === undefined || body.user_id === null) {
						sessionIsInvalid = true;
					} else {
						event.locals.userId = String(body.user_id);
					}
				} catch {
					sessionIsInvalid = true;
				}
			} else {
				sessionIsInvalid = true;
			}
		} catch {
			// Uma falha transitória não deve expor detalhes do backend ao navegador.
		}
	}

	if (sessionIsInvalid) {
		event.cookies.delete('session_id', { path: '/' });
	}

	const isApiRoute = pathname.startsWith('/api/');
	const isPublicPage = ['/login', '/cadastro', '/recuperar-senha', '/reset-password'].some(
		(path) => pathname === path || pathname.startsWith(`${path}/`)
	);
	if (!event.locals.userId && !isApiRoute && !isPublicPage) {
		const next = `${pathname}${event.url.search}`;
		throw redirect(303, `/login?next=${encodeURIComponent(next)}`);
	}

	return resolve(event);
};
