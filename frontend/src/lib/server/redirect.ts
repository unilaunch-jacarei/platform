export function safeInternalRedirect(value: string | null, origin: string): string {
	if (!value || !value.startsWith('/') || value.startsWith('//') || value.startsWith('/\\')) {
		return '/';
	}

	try {
		const target = new URL(value, origin);
		if (target.origin !== new URL(origin).origin) return '/';
		return `${target.pathname}${target.search}${target.hash}`;
	} catch {
		return '/';
	}
}
