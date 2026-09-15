import { fail } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { Actions, PageServerLoad } from './$types';
import { backendFetch } from '$lib/server/backend';
import type { LeadFormValues } from '$lib/lead-form';
import { buildLeadPayload, getBackendError, getLeadErrorStatus, normalizeLeadSource, readLeadForm, validateLeadForm } from '$lib/server/lead-capture';
import { createClientIpHeaders } from '$lib/server/client-ip';

const getRequestId = (request: Request) => request.headers.get('X-Request-ID') ?? crypto.randomUUID();

export const load: PageServerLoad = async ({ url, request, getClientAddress }) => {
	const source = normalizeLeadSource(url.searchParams.get('o'));

	try {
		await backendFetch(`/api/v1/public/leads/views?o=${encodeURIComponent(source)}`, {
			method: 'POST',
			headers: {
				'Idempotency-Key': crypto.randomUUID(),
				...createClientIpHeaders(getClientAddress(), env.INTERNAL_SECRET ?? ''),
				'X-Request-ID': getRequestId(request)
			}
		}).then((response) => {
			if (!response.ok) console.warn('lead_view_tracking_failed', response.status);
		});
	} catch {
		// A tracking failure must not block the public form.
	}

	return { source };
};

export const actions: Actions = {
	default: async ({ request, url, getClientAddress }) => {
		const values: LeadFormValues = readLeadForm(await request.formData());

		if (validateLeadForm(values)) {
			return fail(400, {
				error: 'Preencha os campos obrigatórios e aceite a política de privacidade.',
				values
			});
		}

		try {
			const source = normalizeLeadSource(url.searchParams.get('o'));
			const response = await backendFetch(`/api/v1/public/leads?o=${encodeURIComponent(source)}`, {
				method: 'POST',
				headers: {
					'content-type': 'application/json',
					...createClientIpHeaders(getClientAddress(), env.INTERNAL_SECRET ?? ''),
					'X-Request-ID': getRequestId(request)
				},
				body: JSON.stringify(buildLeadPayload(values))
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				return fail(getLeadErrorStatus(response.status), {
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
