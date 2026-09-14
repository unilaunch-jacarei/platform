export type SessionResolution<User> =
	| { status: 'authenticated'; user: User }
	| { status: 'invalid' }
	| { status: 'unavailable' };

export async function resolveSession<User extends { id?: string }>(
	token: string,
	fetchUser: (token: string) => Promise<Response>
): Promise<SessionResolution<User>> {
	try {
		const response = await fetchUser(token);
		if (response.status === 401 || response.status === 403) return { status: 'invalid' };
		if (!response.ok) return { status: 'unavailable' };

		const user = (await response.json()) as User;
		return user?.id ? { status: 'authenticated', user } : { status: 'unavailable' };
	} catch {
		return { status: 'unavailable' };
	}
}
