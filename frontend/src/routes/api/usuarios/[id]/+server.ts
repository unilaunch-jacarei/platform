import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendFetch } from '$lib/server/backend';

export const GET: RequestHandler = async ({ params, locals }) => {
	// `locals.userId` deve ser preenchido pelo hook após validar a sessão do usuário.
	if (!locals.userId) {
		return json({ error: 'não autenticado' }, { status: 401 });
	}

	const path = `/api/v1/usuarios/${encodeURIComponent(params.id)}`;
	const response = await backendFetch(path, locals.userId);
	const body = await response.json().catch(() => ({ error: 'resposta inválida do backend' }));

	return json(body, { status: response.status });
};
