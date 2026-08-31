import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendFetch } from '$lib/server/backend';

export const GET: RequestHandler = async ({ params, locals }) => {
	if (!locals.token) {
		return json({ error: 'não autenticado' }, { status: 401 });
	}

	const path = `/api/v1/usuarios/${encodeURIComponent(params.id)}`;
	const response = await backendFetch(path, locals.token);
	const body = await response.json().catch(() => ({ error: 'resposta inválida do backend' }));

	return json(body, { status: response.status });
};
