import { env } from '$env/dynamic/private';

const backendUrl = env.BACKEND_URL ?? 'http://127.0.0.1:3000';

/** Faz requests server-to-server autenticadas contra o Resource Server Rust. */
export async function backendFetch(
	path: string,
	userId: string,
	init: RequestInit = {}
): Promise<Response> {
	if (!env.INTERNAL_SECRET) {
		throw new Error('INTERNAL_SECRET não configurada no SvelteKit');
	}

	const timestamp = Math.floor(Date.now() / 1000).toString();
	const payload = `${timestamp}:${path}:${userId}`;
	const key = await crypto.subtle.importKey(
		'raw',
		new TextEncoder().encode(env.INTERNAL_SECRET),
		{ name: 'HMAC', hash: 'SHA-256' },
		false,
		['sign']
	);
	const digest = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(payload));
	const signature = [...new Uint8Array(digest)]
		.map((byte) => byte.toString(16).padStart(2, '0'))
		.join('');
	const headers = new Headers(init.headers);
	headers.set('x-user-id', userId);
	headers.set('x-timestamp', timestamp);
	headers.set('x-signature', signature);

	return fetch(new URL(path, backendUrl), { ...init, headers });
}
