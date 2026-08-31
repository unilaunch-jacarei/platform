import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';
import { backendFetch } from '$lib/server/backend';

export const actions: Actions = {
	default: async ({ request }) => {
		const form = await request.formData();
		const email = String(form.get('email') ?? '').trim();

		if (!email) {
			return fail(400, { error: 'Informe seu e-mail.', email });
		}

		try {
			const response = await backendFetch('/api/v1/auth/forgot-password', {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ email })
			});

			if (!response.ok) {
				return fail(400, { error: 'Não foi possível solicitar a recuperação.', email });
			}
		} catch {
			return fail(503, { error: 'Não foi possível conectar ao servidor.', email });
		}

		return { success: true };
	}
};
