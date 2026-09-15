import type { LeadFormValues, StudentLeadFormValues } from '$lib/lead-form';

export function readLeadForm(form: FormData): LeadFormValues {
	return {
		full_name: String(form.get('full_name') ?? '').trim(),
		email: String(form.get('email') ?? '').trim(),
		company_name: String(form.get('company_name') ?? '').trim(),
		job_title: String(form.get('job_title') ?? '').trim(),
		company_size: String(form.get('company_size') ?? '').trim(),
		website: String(form.get('website') ?? '').trim(),
		message: String(form.get('message') ?? '').trim(),
		privacy_consent: form.get('privacy_consent') === 'on'
	};
}

export function validateLeadForm(values: LeadFormValues): string | undefined {
	if (!values.full_name || !values.email || !values.company_name || !values.privacy_consent) {
		return 'Preencha os campos obrigatórios e aceite a política de privacidade.';
	}
}

export function buildLeadPayload(values: LeadFormValues): LeadFormValues {
	const optional = (value?: string) => value || undefined;
	return {
		...values,
		job_title: optional(values.job_title),
		company_size: optional(values.company_size),
		website: optional(values.website),
		message: optional(values.message)
	};
}

export function readStudentLeadForm(form: FormData): StudentLeadFormValues {
	return {
		full_name: String(form.get('full_name') ?? '').trim(),
		email: String(form.get('email') ?? '').trim(),
		institution_name: String(form.get('institution_name') ?? '').trim(),
		course_name: String(form.get('course_name') ?? '').trim(),
		semester: String(form.get('semester') ?? '').trim(),
		linkedin_url: String(form.get('linkedin_url') ?? '').trim(),
		github_url: String(form.get('github_url') ?? '').trim(),
		area_of_interest: String(form.get('area_of_interest') ?? '').trim(),
		message: String(form.get('message') ?? '').trim(),
		privacy_consent: form.get('privacy_consent') === 'on'
	};
}

export function validateStudentLeadForm(values: StudentLeadFormValues): string | undefined {
	if (!values.full_name || !values.email || !values.institution_name || !values.course_name || !values.privacy_consent) {
		return 'Preencha os campos obrigatórios e aceite a política de privacidade.';
	}
}

export function buildStudentLeadPayload(values: StudentLeadFormValues): StudentLeadFormValues {
	const optional = (value?: string) => value || undefined;
	return {
		...values,
		semester: optional(values.semester),
		linkedin_url: optional(values.linkedin_url),
		github_url: optional(values.github_url),
		area_of_interest: optional(values.area_of_interest),
		message: optional(values.message)
	};
}

export function getBackendError(body: unknown): string | undefined {
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
}

export function getLeadErrorStatus(status: number): 400 | 429 | 503 {
	if (status === 429) return 429;
	if (status >= 500) return 503;
	return 400;
}

export function normalizeLeadSource(source: string | null): string {
	return (source?.trim() || 'direct').slice(0, 255);
}
