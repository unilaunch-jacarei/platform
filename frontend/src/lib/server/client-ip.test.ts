import { describe, expect, test } from 'bun:test';
import { createClientIpHeaders } from './client-ip';

describe('createClientIpHeaders', () => {
	test('signs the client IP for the backend', () => {
		expect(createClientIpHeaders('203.0.113.10', 'secret')).toEqual({
			'X-Client-IP': '203.0.113.10',
			'X-Client-IP-Signature':
				'81b5173040f9855425a0e46a692d796dc359a261af055674a7ab719c40427fd3'
		});
	});

	test('requires the internal secret', () => {
		expect(() => createClientIpHeaders('203.0.113.10', '')).toThrow('INTERNAL_SECRET');
	});
});
