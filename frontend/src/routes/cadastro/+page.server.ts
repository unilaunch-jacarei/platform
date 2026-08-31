import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { backendFetch } from '$lib/server/backend';

export const actions: Actions = {
	default: async ({ request, cookies }) => {
		const form = await request.formData();

		const nome = String(form.get('nome') ?? '').trim();
		const email = String(form.get('email') ?? '').trim();
		const password = String(form.get('password') ?? '');

		if (!nome || !email || !password) {
			return fail(400, {
				error: 'Preencha todos os campos.',
				nome,
				email
			});
		}

		if (password.length < 8) {
			return fail(400, {
				error: 'A senha deve possuir pelo menos 8 caracteres.',
				nome,
				email
			});
		}

		try {
			// 1. Cadastrar usuário no backend
			const response = await backendFetch('/api/v1/auth/register', {
				method: 'POST',
				headers: {
					'content-type': 'application/json'
				},
				body: JSON.stringify({
					nome,
					email,
					password
				})
			});

			if (!response.ok) {
				const errorData = (await response.json().catch(() => ({}))) as {
					code?: string;
					error?: string;
					detail?: string;
				};
				if (
					errorData.code === 'REGISTER_USER_ALREADY_EXISTS' ||
					errorData.detail === 'REGISTER_USER_ALREADY_EXISTS'
				) {
					return fail(400, {
						error: 'Este e-mail já está cadastrado.',
						nome,
						email
					});
				}
				return fail(400, {
					error: errorData.error || errorData.detail || 'Não foi possível criar a conta.',
					nome,
					email
				});
			}

			// 2. Fazer login automático pós-cadastro
			const loginParams = new URLSearchParams();
			loginParams.append('username', email);
			loginParams.append('password', password);

			const loginResponse = await backendFetch('/api/v1/auth/jwt/login', {
				method: 'POST',
				headers: {
					'content-type': 'application/x-www-form-urlencoded'
				},
				body: loginParams.toString()
			});

			if (loginResponse.ok) {
				const body = (await loginResponse.json()) as { access_token: string };
				cookies.set('session_token', body.access_token, {
					path: '/',
					httpOnly: true,
					secure: !import.meta.env.DEV,
					sameSite: 'lax',
					maxAge: 60 * 60 * 24 * 7 // 7 dias
				});
				throw redirect(303, '/');
			}
		} catch (err) {
			if (err && typeof err === 'object' && 'status' in err && (err as { status: number }).status === 303) {
				throw err;
			}
			return fail(503, {
				error: 'Serviço de backend indisponível no momento.',
				nome,
				email
			});
		}

		throw redirect(303, '/login');
	}
};
