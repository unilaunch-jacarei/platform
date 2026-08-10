import { json } from '@sveltejs/kit';
import { dev } from '$app/environment';
import type { RequestHandler } from './$types';
import { backendFetch } from '$lib/server/backend';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { email, password } = await request.json().catch(() => ({}));
	if (typeof email !== 'string' || typeof password !== 'string') {
		return json({ error: 'e-mail e senha são obrigatórios' }, { status: 400 });
	}

	const response = await backendFetch('/api/v1/auth/login', email, {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify({ email, password })
	});
	const body = await response.json().catch(() => ({ error: 'resposta inválida do backend' }));

	if (!response.ok) return json({ error: 'e-mail ou senha inválidos' }, { status: 401 });

	cookies.set('session_id', body.session_id, {
		path: '/',
		httpOnly: true,
		secure: !dev,
		sameSite: 'strict',
		maxAge: 60 * 60 * 8
	});
	return json({ user_id: body.user_id });
};
