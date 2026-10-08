import { createHmac } from 'node:crypto';

export function createClientIpHeaders(clientIp: string, secret: string): Record<string, string> {
	if (!secret) throw new Error('INTERNAL_SECRET is required');

	return {
		'X-Client-IP': clientIp,
		'X-Client-IP-Signature': createHmac('sha256', secret).update(clientIp).digest('hex')
	};
}
