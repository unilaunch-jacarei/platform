import { describe, expect, test } from 'bun:test';
import { safeInternalRedirect } from './redirect';

const origin = 'https://unilaunch.org';

describe('safeInternalRedirect', () => {
	test('preserva caminho interno, busca e fragmento', () => {
		expect(safeInternalRedirect('/projetos?filtro=meus#ativos', origin)).toBe(
			'/projetos?filtro=meus#ativos'
		);
	});

	test.each([
		'https://exemplo.com/phishing',
		'//exemplo.com/phishing',
		'/\\exemplo.com/phishing',
		'projetos',
		'http://[url-invalida'
	])('substitui destino inseguro %s pela raiz', (value: string) => {
		expect(safeInternalRedirect(value, origin)).toBe('/');
	});
});
