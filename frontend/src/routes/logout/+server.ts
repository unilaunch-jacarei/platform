import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendFetch } from '$lib/server/backend';

export const POST: RequestHandler = async ({ cookies }) => {
	const sessionToken = cookies.get('session_token');
	if (sessionToken) {
		await backendFetch('/api/v1/auth/jwt/logout', sessionToken, { method: 'POST' }).catch(() => undefined);
	}

	cookies.delete('session_token', { path: '/' });
	throw redirect(303, '/login');
};

export const GET: RequestHandler = async ({ cookies }) => {
	const sessionToken = cookies.get('session_token');
	if (sessionToken) {
		await backendFetch('/api/v1/auth/jwt/logout', sessionToken, { method: 'POST' }).catch(() => undefined);
	}

	cookies.delete('session_token', { path: '/' });
	throw redirect(303, '/login');
};
