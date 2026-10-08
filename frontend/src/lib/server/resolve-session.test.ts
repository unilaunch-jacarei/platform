import { describe, expect, test } from 'bun:test';
import { resolveSession } from './resolve-session';

const response = (status: number, body: unknown = {}) =>
	new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

describe('resolveSession', () => {
	test('autentica uma resposta válida', async () => {
		expect(await resolveSession('token', async () => response(200, { id: 'usuario-1' }))).toEqual({
			status: 'authenticated',
			user: { id: 'usuario-1' }
		});
	});

	test.each([401, 403])('invalida a sessão com status %s', async (status: number) => {
		expect(await resolveSession('token', async () => response(status))).toEqual({ status: 'invalid' });
	});

	test.each([429, 500])('preserva a sessão com falha transitória %s', async (status: number) => {
		expect(await resolveSession('token', async () => response(status))).toEqual({ status: 'unavailable' });
	});

	test('preserva a sessão quando a rede falha', async () => {
		expect(
			await resolveSession('token', async () => {
				throw new Error('falha de rede');
			})
		).toEqual({ status: 'unavailable' });
	});
});
