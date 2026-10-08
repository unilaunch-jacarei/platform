import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { authenticateWithPassword, setSessionCookie, type LoginResult } from '$lib/server/session';
import { safeInternalRedirect } from '$lib/server/redirect';

export const actions: Actions = {
	default: async ({ request, cookies, url }) => {
		const form = await request.formData();
		const email = String(form.get('email') ?? '').trim();
		const password = String(form.get('password') ?? '');
		const remember = form.get('remember') === 'on';

		if (!email || !password) {
			return fail(400, { error: 'Informe seu e-mail e sua senha.', email });
		}

		try {
			const response = await authenticateWithPassword(email, password);

			if (!response.ok) {
				return fail(401, { error: 'E-mail ou senha inválidos.', email });
			}

			const body = (await response.json()) as LoginResult;
			setSessionCookie(cookies, body.access_token, remember);
		} catch {
			return fail(503, { error: 'Não foi possível conectar ao servidor.', email });
		}

		throw redirect(303, safeInternalRedirect(url.searchParams.get('next'), url.origin));
	}
};
