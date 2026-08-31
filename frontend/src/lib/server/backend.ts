import { env } from '$env/dynamic/private';

export const BACKEND_URL = env.BACKEND_URL ?? 'http://127.0.0.1:3000';

/**
 * Faz requests server-to-server seguras contra a API FastAPI do backend.
 * Encaminha o Bearer token JWT diretamente do servidor SvelteKit,
 * garantindo que o token nunca seja exposto ao JavaScript do navegador.
 */
export async function backendFetch(
	path: string,
	tokenOrInit?: string | RequestInit,
	init?: RequestInit
): Promise<Response> {
	let token: string | undefined;
	let requestInit: RequestInit = {};

	if (typeof tokenOrInit === 'string') {
		token = tokenOrInit;
		requestInit = init ?? {};
	} else if (tokenOrInit) {
		requestInit = tokenOrInit;
	}

	const headers = new Headers(requestInit.headers);

	if (token) {
		headers.set('authorization', `Bearer ${token}`);
	}

	const targetUrl = new URL(path, BACKEND_URL);
	return fetch(targetUrl, {
		...requestInit,
		headers
	});
}
