import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { backendFetch } from '$lib/server/backend';

export type HomePriority = 'low' | 'medium' | 'high' | 'urgent';

export type HomeTask = {
	id: string;
	column_id: string;
	title: string;
	description: string | null;
	priority: HomePriority;
	due_date: string | null;
	position: number;
};

export type HomeColumn = {
	id: string;
	name: string;
	position: number;
	tasks: HomeTask[];
};

export type HomeBoard = {
	id: string;
	title: string;
	description: string | null;
	columns: HomeColumn[];
};

const PRIORITIES: HomePriority[] = ['low', 'medium', 'high', 'urgent'];

type BackendRecord = Record<string, unknown>;

function asRecord(value: unknown): BackendRecord | null {
	return value && typeof value === 'object' ? (value as BackendRecord) : null;
}

function parseTask(payload: unknown): HomeTask | null {
	const task = asRecord(payload);
	if (!task || typeof task.id !== 'string' || typeof task.column_id !== 'string' || typeof task.title !== 'string') {
		return null;
	}

	const priority = PRIORITIES.includes(task.priority as HomePriority)
		? (task.priority as HomePriority)
		: 'medium';

	return {
		id: task.id,
		column_id: task.column_id,
		title: task.title,
		description: typeof task.description === 'string' ? task.description : null,
		priority,
		due_date: typeof task.due_date === 'string' ? task.due_date : null,
		position: typeof task.position === 'number' ? task.position : 0
	};
}

function parseColumn(payload: unknown): HomeColumn | null {
	const column = asRecord(payload);
	if (!column || typeof column.id !== 'string' || typeof column.name !== 'string') {
		return null;
	}

	const tasks = Array.isArray(column.tasks)
		? column.tasks.flatMap((item) => {
				const task = parseTask(item);
				return task ? [task] : [];
			})
		: [];

	return {
		id: column.id,
		name: column.name,
		position: typeof column.position === 'number' ? column.position : 0,
		tasks: tasks.sort((left, right) => left.position - right.position)
	};
}

function parseBoard(payload: unknown): HomeBoard | null {
	const board = asRecord(payload);
	if (!board || typeof board.id !== 'string' || typeof board.title !== 'string') {
		return null;
	}

	const columns = Array.isArray(board.columns)
		? board.columns.flatMap((item) => {
				const column = parseColumn(item);
				return column ? [column] : [];
			})
		: [];

	return {
		id: board.id,
		title: board.title,
		description: typeof board.description === 'string' ? board.description : null,
		columns: columns.sort((left, right) => left.position - right.position)
	};
}

function requireToken(token: string | undefined): string {
	if (!token) redirect(303, '/login');
	return token;
}

export const load: PageServerLoad = async ({ locals }) => {
	const token = requireToken(locals.token);

	try {
		const response = await backendFetch('/api/v1/boards', token);
		if (!response.ok) {
			return { board: null, unavailable: true };
		}

		const payload: unknown = await response.json().catch(() => []);
		const boards = Array.isArray(payload)
			? payload.flatMap((item) => {
					const board = parseBoard(item);
					return board ? [board] : [];
				})
			: [];

		return { board: boards[0] ?? null, unavailable: false };
	} catch {
		return { board: null, unavailable: true };
	}
};
