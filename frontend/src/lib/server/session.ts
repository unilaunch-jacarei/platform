import { dev } from '$app/environment';
import type { Cookies } from '@sveltejs/kit';
import { backendFetch } from '$lib/server/backend';

const SESSION_COOKIE = 'session_token';
const SESSION_MAX_AGE = 60 * 60 * 24 * 7;

export type LoginResult = {
	access_token: string;
	token_type?: string;
};

export function authenticateWithPassword(email: string, password: string): Promise<Response> {
	const credentials = new URLSearchParams({ username: email, password });

	return backendFetch('/api/v1/auth/jwt/login', {
		method: 'POST',
		headers: { 'content-type': 'application/x-www-form-urlencoded' },
		body: credentials.toString()
	});
}

export function setSessionCookie(cookies: Cookies, token: string): void {
	cookies.set(SESSION_COOKIE, token, {
		path: '/',
		httpOnly: true,
		secure: !dev,
		sameSite: 'lax',
		maxAge: SESSION_MAX_AGE
	});
}

export async function clearSession(cookies: Cookies): Promise<void> {
	const token = cookies.get(SESSION_COOKIE);
	if (token) {
		await backendFetch('/api/v1/auth/jwt/logout', token, { method: 'POST' }).catch(() => undefined);
	}

	cookies.delete(SESSION_COOKIE, { path: '/' });
}
