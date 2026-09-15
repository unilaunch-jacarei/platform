import { env } from '$env/dynamic/private';
import { json } from '@sveltejs/kit';
import { backendFetch } from '$lib/server/backend';
import { createClientIpHeaders } from '$lib/server/client-ip';
import type { RequestHandler } from './$types';

const catalogs = new Set(['institutions', 'courses']);

export const GET: RequestHandler = async ({ params, url, request, getClientAddress }) => {
	if (!catalogs.has(params.catalog)) {
		return json({ error: 'Catálogo não encontrado.' }, { status: 404 });
	}
	const query = url.searchParams.get('q')?.trim() ?? '';
	if (query.length < 2) return json([]);

	try {
		const response = await backendFetch(
			`/api/v1/public/leads/catalog/${params.catalog}?q=${encodeURIComponent(query)}`,
			{
				headers: {
					...createClientIpHeaders(getClientAddress(), env.INTERNAL_SECRET ?? ''),
					'X-Request-ID': request.headers.get('X-Request-ID') ?? crypto.randomUUID()
				}
			}
		);
		const body = await response.json().catch(() => ({ error: 'Resposta inválida do serviço.' }));
		return json(body, {
			status: response.status,
			headers: response.ok ? { 'cache-control': 'public, max-age=60' } : undefined
		});
	} catch {
		return json({ error: 'Serviço indisponível no momento.' }, { status: 503 });
	}
};
