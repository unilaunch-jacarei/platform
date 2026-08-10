import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { backendFetch } from "$lib/server/backend";

export const actions: Actions = {
    default: async ({ request }) => {
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
                error: 'A senha deve possuir pelo menos 8 caracteres',
                nome,
                email
            });
        }

        try {
            const response = await backendFetch('/api/v1/usuarios', email, {
                method: 'POST',
                headers: {
                    'content-type': 'application/json'
                },
                body: JSON.stringify({
                    nome, email, password
                })
            });

            if (!response.ok) {
                return fail(400, {
                    error: 'Não foi possível criar a conta.',
                    nome,
                    email
                });
            }
        } catch {
            return fail(503, {
                error: 'Backend indisponível.',
                nome,
                email
            });
        }

        throw redirect(303, '/login');
    }
}
