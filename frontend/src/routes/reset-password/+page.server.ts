import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { backendFetch } from '$lib/server/backend';

export const load: PageServerLoad = ({ url }) => ({
	token: url.searchParams.get('token') ?? ''
});

export const actions: Actions = {
	default: async ({ request }) => {
		const form = await request.formData();
		const token = String(form.get('token') ?? '').trim();
		const password = String(form.get('password') ?? '');
		const confirmation = String(form.get('confirmation') ?? '');

		if (!token) {
			return fail(400, {
				error: 'O link de recuperação é inválido.',
				errors: { password: undefined, confirmation: undefined }
			});
		}
		if (password.length < 8) {
			return fail(400, {
				error: 'A nova senha deve ter pelo menos 8 caracteres.',
				errors: { password: 'Use pelo menos 8 caracteres.', confirmation: undefined }
			});
		}
		if (password !== confirmation) {
			return fail(400, {
				error: 'Revise os dados informados.',
				errors: { password: undefined, confirmation: 'As senhas não conferem.' }
			});
		}

		try {
			const response = await backendFetch('/api/v1/auth/reset-password', {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ token, password })
			});

			if (response.status === 400 || response.status === 401) {
				return fail(400, {
					error: 'Este link é inválido, expirou ou já foi utilizado.',
					errors: { password: undefined, confirmation: undefined }
				});
			}
			if (!response.ok) {
				return fail(502, {
					error: 'Não foi possível redefinir sua senha.',
					errors: { password: undefined, confirmation: undefined }
				});
			}
		} catch {
			return fail(503, {
				error: 'Não foi possível conectar ao servidor.',
				errors: { password: undefined, confirmation: undefined }
			});
		}

		throw redirect(303, '/login?reset=success');
	}
};
