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
			const bodyParams = new URLSearchParams();
			bodyParams.append('username', email);
			bodyParams.append('password', password);

			const response = await backendFetch('/api/v1/auth/jwt/login', {
				method: 'POST',
				headers: {
					'content-type': 'application/x-www-form-urlencoded'
				},
				body: bodyParams.toString()
			});

			if (!response.ok) {
				return fail(401, { error: 'E-mail ou senha inválidos.', email });
			}

			const body = (await response.json()) as { access_token: string; token_type: string };

			cookies.set('session_token', body.access_token, {
				path: '/',
				httpOnly: true,
				secure: !import.meta.env.DEV,
				sameSite: 'lax',
				maxAge: 60 * 60 * 24 * 7 // 7 dias
			});
		} catch {
			return fail(503, { error: 'Não foi possível conectar ao servidor.', email });
		}

		const next = url.searchParams.get('next');
		throw redirect(303, next?.startsWith('/') ? next : '/');
	}
};
