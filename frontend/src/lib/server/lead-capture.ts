import type { LeadFormValues, StudentLeadFormValues, StudentLeadPayload } from '$lib/lead-form';

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
		institution_id: String(form.get('institution_id') ?? '').trim(),
		institution_name: String(form.get('institution_name') ?? '').trim(),
		institution_name_display: String(form.get('institution_name_display') ?? '').trim(),
		course_id: String(form.get('course_id') ?? '').trim(),
		course_name: String(form.get('course_name') ?? '').trim(),
		course_name_display: String(form.get('course_name_display') ?? '').trim(),
		semester_number: String(form.get('semester_number') ?? '').trim(),
		linkedin_url: String(form.get('linkedin_url') ?? '').trim(),
		github_url: String(form.get('github_url') ?? '').trim(),
		interest_area_ids: form.getAll('interest_area_ids').map(String).filter(Boolean),
		message: String(form.get('message') ?? '').trim(),
		privacy_consent: form.get('privacy_consent') === 'on'
	};
}

export function validateStudentLeadForm(values: StudentLeadFormValues): string | undefined {
	const hasInstitution = Boolean(values.institution_id) !== Boolean(values.institution_name);
	const hasCourse = Boolean(values.course_id) !== Boolean(values.course_name);
	if (!values.full_name || !values.email || !hasInstitution || !hasCourse || !values.privacy_consent) {
		return 'Preencha os campos obrigatórios e aceite a política de privacidade.';
	}
	if (values.semester_number && !/^(?:[1-9]|1[0-2])$/.test(values.semester_number)) {
		return 'Selecione um semestre válido entre 1 e 12.';
	}
	const areaIds = values.interest_area_ids ?? [];
	if (areaIds.length > 3 || new Set(areaIds).size !== areaIds.length) {
		return 'Escolha no máximo três áreas de interesse diferentes.';
	}
}

export function buildStudentLeadPayload(values: StudentLeadFormValues): StudentLeadPayload {
	const optional = (value?: string) => value || undefined;
	return {
		full_name: values.full_name,
		email: values.email,
		institution_id: optional(values.institution_id),
		institution_name: values.institution_id ? undefined : optional(values.institution_name),
		course_id: optional(values.course_id),
		course_name: values.course_id ? undefined : optional(values.course_name),
		semester_number: values.semester_number ? Number(values.semester_number) : undefined,
		linkedin_url: optional(values.linkedin_url),
		github_url: optional(values.github_url),
		interest_area_ids: values.interest_area_ids ?? [],
		message: optional(values.message),
		privacy_consent: values.privacy_consent
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
