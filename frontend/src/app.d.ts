export interface User {
	id: string;
	email: string;
	nome: string;
	is_active?: boolean;
	is_superuser?: boolean;
	is_verified?: boolean;
}

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			user: User | null;
			userId?: string;
			token?: string;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
