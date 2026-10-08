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
		form.set('semester_number', '4');
		form.append('interest_area_ids', 'area-1');
		form.append('interest_area_ids', 'area-2');
		form.set('privacy_consent', 'on');

		const values = readStudentLeadForm(form);
		expect(values.institution_name).toBe('Fatec Jacareí');
		expect(values.interest_area_ids).toEqual(['area-1', 'area-2']);
		expect(validateStudentLeadForm(values)).toBeUndefined();
		const payload = buildStudentLeadPayload(values);
		expect(payload.github_url).toBeUndefined();
		expect(payload.semester_number).toBe(4);
		expect(payload.interest_area_ids).toEqual(['area-1', 'area-2']);
		expect(validateStudentLeadForm({})).toContain('campos obrigatórios');
	});

	test('restores selected catalogs without sending display names', () => {
		const form = new FormData();
		form.set('full_name', 'Grace Hopper');
		form.set('email', 'grace@example.com');
		form.set('institution_id', 'institution-id');
		form.set('institution_name_display', 'Universidade Canônica');
		form.set('course_id', 'course-id');
		form.set('course_name_display', 'Curso Canônico');
		form.set('privacy_consent', 'on');

		const values = readStudentLeadForm(form);
		expect(validateStudentLeadForm(values)).toBeUndefined();
		expect(buildStudentLeadPayload(values)).toEqual({
			full_name: 'Grace Hopper',
			email: 'grace@example.com',
			institution_id: 'institution-id',
			institution_name: undefined,
			course_id: 'course-id',
			course_name: undefined,
			semester_number: undefined,
			linkedin_url: undefined,
			github_url: undefined,
			interest_area_ids: [],
			message: undefined,
			privacy_consent: true
		});
	});

	test('rejects invalid semester and interest area selections', () => {
		const base = {
			full_name: 'Ada Lovelace',
			email: 'ada@example.com',
			institution_name: 'Universidade',
			course_name: 'Computação',
			privacy_consent: true
		};
		expect(validateStudentLeadForm({ ...base, semester_number: '4.5' })).toContain('semestre');
		expect(
			validateStudentLeadForm({ ...base, interest_area_ids: ['1', '2', '3', '4'] })
		).toContain('três áreas');
		expect(validateStudentLeadForm({ ...base, interest_area_ids: ['1', '1'] })).toContain(
			'três áreas'
		);
	});
});
