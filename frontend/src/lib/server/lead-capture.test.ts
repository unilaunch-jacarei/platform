import { describe, expect, test } from 'bun:test';
import { buildLeadPayload, buildStudentLeadPayload, getBackendError, getLeadErrorStatus, normalizeLeadSource, readLeadForm, readStudentLeadForm, validateLeadForm, validateStudentLeadForm } from './lead-capture';

describe('lead capture helpers', () => {
	test('normalizes form data and keeps required fields', () => {
		const form = new FormData();
		form.set('full_name', ' Ada Lovelace ');
		form.set('email', 'ada@example.com');
		form.set('company_name', ' Analytical Engines ');
		form.set('privacy_consent', 'on');

		const values = readLeadForm(form);
		expect(values.full_name).toBe('Ada Lovelace');
		expect(values.company_name).toBe('Analytical Engines');
		expect(validateLeadForm(values)).toBeUndefined();
	});

	test('omits empty optional fields from backend payload', () => {
		const payload = buildLeadPayload({
			full_name: 'Ada Lovelace',
			email: 'ada@example.com',
			company_name: 'Analytical Engines',
			job_title: '',
			company_size: '',
			website: '',
			message: '',
			privacy_consent: true
		});

		expect(payload.job_title).toBeUndefined();
		expect(payload.company_size).toBeUndefined();
		expect(payload.website).toBeUndefined();
		expect(payload.message).toBeUndefined();
	});

	test('requires required fields and privacy consent', () => {
		expect(validateLeadForm({})).toContain('campos obrigatórios');
	});

	test('reads backend errors in all supported formats', () => {
		expect(getBackendError({ error: 'Erro interno' })).toBe('Erro interno');
		expect(getBackendError({ detail: 'Erro simples' })).toBe('Erro simples');
		expect(getBackendError({ detail: [{ msg: 'Campo inválido' }] })).toBe('Campo inválido');
		expect(getBackendError({ detail: [{ loc: ['email'] }] })).toBeUndefined();
	});

	test('preserves operational error status', () => {
		expect(getLeadErrorStatus(422)).toBe(400);
		expect(getLeadErrorStatus(429)).toBe(429);
		expect(getLeadErrorStatus(500)).toBe(503);
	});

	test('normalizes and limits the lead source', () => {
		expect(normalizeLeadSource(null)).toBe('direct');
		expect(normalizeLeadSource('   ')).toBe('direct');
		expect(normalizeLeadSource('  campaign  ')).toBe('campaign');
		expect(normalizeLeadSource('a'.repeat(300))).toHaveLength(255);
	});

	test('reads and validates a student lead', () => {
		const form = new FormData();
		form.set('full_name', '  Katherine Johnson ');
		form.set('email', 'katherine@example.com');
		form.set('institution_name', ' Fatec Jacareí ');
		form.set('course_name', 'DSM');
		form.set('privacy_consent', 'on');

		const values = readStudentLeadForm(form);
		expect(values.institution_name).toBe('Fatec Jacareí');
		expect(validateStudentLeadForm(values)).toBeUndefined();
		expect(buildStudentLeadPayload(values).github_url).toBeUndefined();
		expect(validateStudentLeadForm({})).toContain('campos obrigatórios');
	});
});
