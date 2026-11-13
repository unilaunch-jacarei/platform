import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
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
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

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

async function backendError(response: Response): Promise<string> {
	if (response.status === 401 || response.status === 403) {
		return 'Sua sessão expirou. Entre novamente para continuar.';
	}
	if (response.status === 404) {
		return 'A tarefa selecionada não existe mais.';
	}
	if (response.status >= 500) {
		return 'Não foi possível salvar a tarefa agora. Tente novamente em instantes.';
	}

	try {
		const body = (await response.json()) as { error?: unknown; detail?: unknown };
		if (typeof body.error === 'string') return body.error;
		if (typeof body.detail === 'string') return body.detail;
	} catch {
		/* A resposta pode não conter JSON. */
	}

	return 'Não foi possível salvar a tarefa. Confira os dados e tente novamente.';
}

export const actions: Actions = {
	create: async ({ request, locals }) => {
		const token = requireToken(locals.token);
		const formData = await request.formData();
		const title = String(formData.get('title') ?? '').trim();
		const description = String(formData.get('description') ?? '').trim();
		const columnId = String(formData.get('column_id') ?? '');
		const rawPriority = String(formData.get('priority') ?? 'medium');
		const priority = PRIORITIES.includes(rawPriority as HomePriority)
			? (rawPriority as HomePriority)
			: 'medium';
		const values = { title, description, column_id: columnId, priority };

		if (!title) {
			return fail(400, { error: 'Informe um título para a tarefa.', values });
		}
		if (title.length > 255) {
			return fail(400, { error: 'O título pode ter no máximo 255 caracteres.', values });
		}
		if (!UUID_PATTERN.test(columnId)) {
			return fail(400, { error: 'Selecione uma coluna válida.', values });
		}

		try {
			const response = await backendFetch('/api/v1/boards/tasks', token, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({
					column_id: columnId,
					title,
					description: description || null,
					priority
				})
			});
			if (!response.ok) {
				return fail(response.status, { error: await backendError(response), values });
			}
		} catch {
			return fail(503, {
				error: 'Não foi possível conectar ao serviço de tarefas. Tente novamente.',
				values
			});
		}

		return { message: 'Tarefa criada.', success: true };
	},

	move: async ({ request, locals }) => {
		const token = requireToken(locals.token);
		const formData = await request.formData();
		const taskId = String(formData.get('task_id') ?? '');
		const columnId = String(formData.get('column_id') ?? '');

		if (!UUID_PATTERN.test(taskId) || !UUID_PATTERN.test(columnId)) {
			return fail(400, { error: 'Movimentação inválida.' });
		}

		try {
			const response = await backendFetch(`/api/v1/boards/tasks/${taskId}`, token, {
				method: 'PATCH',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ column_id: columnId })
			});
			if (!response.ok) {
				return fail(response.status, { error: await backendError(response) });
			}
		} catch {
			return fail(503, { error: 'Não foi possível mover a tarefa. Tente novamente.' });
		}

		return { message: 'Tarefa movida.' };
	},

	delete: async ({ request, locals }) => {
		const token = requireToken(locals.token);
		const formData = await request.formData();
		const taskId = String(formData.get('task_id') ?? '');

		if (!UUID_PATTERN.test(taskId)) {
			return fail(400, { error: 'Tarefa inválida.' });
		}

		try {
			const response = await backendFetch(`/api/v1/boards/tasks/${taskId}`, token, {
				method: 'DELETE'
			});
			if (!response.ok) {
				return fail(response.status, { error: await backendError(response) });
			}
		} catch {
			return fail(503, { error: 'Não foi possível excluir a tarefa. Tente novamente.' });
		}

		return { message: 'Tarefa excluída.' };
	}
};
