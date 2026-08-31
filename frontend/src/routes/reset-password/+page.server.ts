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
		const newPassword = String(form.get('new_password') ?? '');
		const confirmation = String(form.get('confirmation') ?? '');

		if (!token) return fail(400, { error: 'O link de recuperação é inválido.' });
		if (newPassword.length < 8) {
			return fail(400, { error: 'A nova senha deve ter pelo menos 8 caracteres.' });
		}
		if (newPassword !== confirmation) {
			return fail(400, { error: 'As senhas não conferem.' });
		}

		try {
			const response = await backendFetch('/api/v1/auth/reset-password', {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ token, password: newPassword })
			});

			if (response.status === 400 || response.status === 401) {
				return fail(400, { error: 'Este link é inválido, expirou ou já foi utilizado.' });
			}
			if (!response.ok) return fail(400, { error: 'Não foi possível redefinir sua senha.' });
		} catch {
			return fail(503, { error: 'Não foi possível conectar ao servidor.' });
		}

		throw redirect(303, '/login?reset=success');
	}
};
