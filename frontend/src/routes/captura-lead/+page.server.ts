import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { backendFetch } from '$lib/server/backend';
import type { LeadFormValues } from '$lib/lead-form';

const getSource = (value: string | null) => value ?? 'direct';

export const load: PageServerLoad = async ({ url }) => {
	const source = getSource(url.searchParams.get('o'));

	try {
		await backendFetch(`/api/v1/public/leads/views?o=${encodeURIComponent(source)}`, {
			method: 'POST',
			headers: { 'Idempotency-Key': crypto.randomUUID() }
		});
	} catch {
		// A tracking failure must not block the public form.
	}

	return { source };
};

export const actions: Actions = {
	default: async ({ request, url }) => {
		const form = await request.formData();
		const values: LeadFormValues = {
			full_name: String(form.get('full_name') ?? '').trim(),
			email: String(form.get('email') ?? '').trim(),
			company_name: String(form.get('company_name') ?? '').trim(),
			job_title: String(form.get('job_title') ?? '').trim(),
			company_size: String(form.get('company_size') ?? '').trim(),
			website: String(form.get('website') ?? '').trim(),
			message: String(form.get('message') ?? '').trim()
		};
		const privacyConsent = form.get('privacy_consent') === 'on';

		if (!values.full_name || !values.email || !values.company_name || !privacyConsent) {
			return fail(400, {
				error: 'Preencha os campos obrigatórios e aceite a política de privacidade.',
				values
			});
		}

		try {
			const source = getSource(url.searchParams.get('o'));
			const response = await backendFetch(`/api/v1/public/leads?o=${encodeURIComponent(source)}`, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ ...values, privacy_consent: true })
			});

			if (!response.ok) {
				const errorData = (await response.json().catch(() => ({}))) as {
					error?: string;
					detail?: string;
				};
				return fail(response.status === 429 ? 429 : 400, {
					error: errorData.error || errorData.detail || 'Não foi possível enviar seus dados.',
					values
				});
			}

			return { success: true };
		} catch {
			return fail(503, { error: 'Serviço indisponível no momento.', values });
		}
	}
};
