import { describe, expect, test } from 'bun:test';
import { buildLeadPayload, getBackendError, readLeadForm, validateLeadForm } from './lead-capture';

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
});
