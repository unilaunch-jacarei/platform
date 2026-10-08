import type { SubmitFunction } from '@sveltejs/kit';

export type FormState = {
	error?: string;
	message?: string;
	success?: boolean;
	nome?: string;
	email?: string;
	cpf?: string;
	errors?: Record<string, string | undefined>;
} | null;

export function trackFormSubmission(setSubmitting: (value: boolean) => void): SubmitFunction {
	return () => {
		setSubmitting(true);

		return async ({ update }) => {
			try {
				await update();
			} finally {
				setSubmitting(false);
			}
		};
	};
}
