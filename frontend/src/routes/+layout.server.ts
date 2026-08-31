import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = ({ locals }) => ({
	user: locals.user ?? null,
	userId: locals.user?.id ?? null
});
