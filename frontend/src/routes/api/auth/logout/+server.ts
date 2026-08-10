import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendFetch } from '$lib/server/backend';

export const POST: RequestHandler = async ({ cookies }) => {
	const sessionId = cookies.get('session_id');
	if (sessionId) {
		await backendFetch('/api/v1/auth/logout', sessionId, { method: 'DELETE' }).catch(() => undefined);
	}
	cookies.delete('session_id', { path: '/' });
	return json({ ok: true });
};
