import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { authenticateWithPassword, setSessionCookie, type LoginResult } from '$lib/server/session';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { email, password, remember } = await request.json().catch(() => ({}));
	if (typeof email !== 'string' || typeof password !== 'string') {
		return json({ error: 'e-mail e senha são obrigatórios' }, { status: 400 });
	}

	const response = await authenticateWithPassword(email, password);

	if (!response.ok) return json({ error: 'e-mail ou senha inválidos' }, { status: 401 });

	const body = (await response.json()) as LoginResult;
	setSessionCookie(cookies, body.access_token, remember === true);

	return json({ ok: true });
};
