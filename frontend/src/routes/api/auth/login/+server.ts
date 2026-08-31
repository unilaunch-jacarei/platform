import { json } from '@sveltejs/kit';
import { dev } from '$app/environment';
import type { RequestHandler } from './$types';
import { backendFetch } from '$lib/server/backend';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { email, password } = await request.json().catch(() => ({}));
	if (typeof email !== 'string' || typeof password !== 'string') {
		return json({ error: 'e-mail e senha são obrigatórios' }, { status: 400 });
	}

	const bodyParams = new URLSearchParams();
	bodyParams.append('username', email);
	bodyParams.append('password', password);

	const response = await backendFetch('/api/v1/auth/jwt/login', {
		method: 'POST',
		headers: { 'content-type': 'application/x-www-form-urlencoded' },
		body: bodyParams.toString()
	});

	if (!response.ok) return json({ error: 'e-mail ou senha inválidos' }, { status: 401 });

	const body = (await response.json()) as { access_token: string };

	cookies.set('session_token', body.access_token, {
		path: '/',
		httpOnly: true,
		secure: !dev,
		sameSite: 'lax',
		maxAge: 60 * 60 * 24 * 7
	});

	return json({ ok: true });
};
