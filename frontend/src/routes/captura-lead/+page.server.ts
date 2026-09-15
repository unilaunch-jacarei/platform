import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { backendFetch } from '$lib/server/backend';
import type { LeadFormValues } from '$lib/lead-form';

const getSource = (value: string | null) => value ?? 'direct';
const optionalValue = (value: string) => value || undefined;

function getBackendError(body: unknown): string | undefined {
	if (!body || typeof body !== 'object') return undefined;
	const data = body as { error?: unknown; detail?: unknown };
	if (typeof data.error === 'string') return data.error;
	if (typeof data.detail === 'string') return data.detail;
	if (Array.isArray(data.detail)) {
		const messages = data.detail.flatMap((item) => {
			if (item && typeof item === 'object' && 'msg' in item) {
				const message = (item as { msg?: unknown }).msg;
				return typeof message === 'string' ? [message] : [];
			}
			return [];
		});
		return messages.length ? messages.join(' ') : undefined;
	}
	return undefined;
}

export const load: PageServerLoad = async ({ url, getClientAddress }) => {
	const source = getSource(url.searchParams.get('o'));

	try {
		await backendFetch(`/api/v1/public/leads/views?o=${encodeURIComponent(source)}`, {
			method: 'POST',
			headers: {
				'Idempotency-Key': crypto.randomUUID(),
				'X-Forwarded-For': getClientAddress()
			}
		});
	} catch {
		// A tracking failure must not block the public form.
	}

	return { source };
};

export const actions: Actions = {
	default: async ({ request, url, getClientAddress }) => {
		const form = await request.formData();
		const values: LeadFormValues = {
			full_name: String(form.get('full_name') ?? '').trim(),
			email: String(form.get('email') ?? '').trim(),
			company_name: String(form.get('company_name') ?? '').trim(),
			job_title: String(form.get('job_title') ?? '').trim(),
			company_size: String(form.get('company_size') ?? '').trim(),
			website: String(form.get('website') ?? '').trim(),
			message: String(form.get('message') ?? '').trim()
			, privacy_consent: form.get('privacy_consent') === 'on'
		};

		if (!values.full_name || !values.email || !values.company_name || !values.privacy_consent) {
			return fail(400, {
				error: 'Preencha os campos obrigatórios e aceite a política de privacidade.',
				values
			});
		}

		try {
			const source = getSource(url.searchParams.get('o'));
			const response = await backendFetch(`/api/v1/public/leads?o=${encodeURIComponent(source)}`, {
				method: 'POST',
				headers: {
					'content-type': 'application/json',
					'X-Forwarded-For': getClientAddress()
				},
				body: JSON.stringify({
					...values,
					job_title: optionalValue(values.job_title ?? ''),
					company_size: optionalValue(values.company_size ?? ''),
					website: optionalValue(values.website ?? ''),
					message: optionalValue(values.message ?? '')
				})
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				return fail(response.status === 429 ? 429 : 400, {
					error: getBackendError(errorData) || 'Não foi possível enviar seus dados.',
					values
				});
			}

			return { success: true };
		} catch {
			return fail(503, { error: 'Serviço indisponível no momento.', values });
		}
	}
};
