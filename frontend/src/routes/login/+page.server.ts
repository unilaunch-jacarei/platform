import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { backendFetch } from '$lib/server/backend';

export const actions: Actions = {
	default: async ({ request, cookies, url }) => {
		const form = await request.formData();
		const email = String(form.get('email') ?? '').trim();
		const password = String(form.get('password') ?? '');

		if (!email || !password) {
			return fail(400, { error: 'Informe seu e-mail e sua senha.', email });
		}

		try {
			const response = await backendFetch('/api/v1/auth/login', email, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ email, password })
			});

			if (!response.ok) {
				return fail(401, { error: 'E-mail ou senha inválidos.', email });
			}

			const body = await response.json();
			cookies.set('session_id', body.session_id, {
				path: '/',
				httpOnly: true,
				secure: !import.meta.env.DEV,
				sameSite: 'strict',
				maxAge: 60 * 60 * 8
			});
		} catch {
			return fail(503, { error: 'Não foi possível conectar ao servidor.', email });
		}

		const next = url.searchParams.get('next');
		throw redirect(303, next?.startsWith('/') ? next : '/');
	}
};
