import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { backendFetch } from '$lib/server/backend';

type Task = { id: string; title: string; description: string | null; completed: boolean; createdAt: string | null; updatedAt: string | null };
type BackendTask = { id?: unknown; title?: unknown; description?: unknown; completed?: unknown; created_at?: unknown; updated_at?: unknown; update_at?: unknown };

function parseTasks(payload: unknown): Task[] {
	if (!Array.isArray(payload)) return [];
	return payload.flatMap((item) => {
		if (!item || typeof item !== 'object') return [];
		const task = item as BackendTask;
		if (typeof task.id !== 'string' || typeof task.title !== 'string') return [];
		return [{ id: task.id, title: task.title, description: typeof task.description === 'string' ? task.description : null, completed: task.completed === true, createdAt: typeof task.created_at === 'string' ? task.created_at : null, updatedAt: typeof task.updated_at === 'string' ? task.updated_at : typeof task.update_at === 'string' ? task.update_at : null }];
	});
}

function requireToken(token: string | undefined): string {
	if (!token) redirect(303, '/login');
	return token;
}

async function backendError(response: Response): Promise<string> {
	if (response.status === 401 || response.status === 403) return 'Sua sessão expirou. Entre novamente para continuar.';
	if (response.status >= 500) return 'Não foi possível salvar a tarefa agora. Tente novamente em instantes.';
	try {
		const body = (await response.json()) as { detail?: unknown };
		if (typeof body.detail === 'string') return body.detail;
	} catch { /* A resposta pode não conter JSON. */ }
	return 'Não foi possível salvar a tarefa. Confira os dados e tente novamente.';
}

export const load: PageServerLoad = async ({ locals }) => {
	const token = requireToken(locals.token);
	try {
		const response = await backendFetch('/api/v1/tasks', token);
		if (!response.ok) return { tasks: [], pendingTasks: [], completedTasks: [], unavailable: true };
		const tasks = parseTasks(await response.json());
		return { tasks, pendingTasks: tasks.filter((task) => !task.completed), completedTasks: tasks.filter((task) => task.completed), unavailable: false };
	} catch {
		return { tasks: [], pendingTasks: [], completedTasks: [], unavailable: true };
	}
};

export const actions: Actions = {
	create: async ({ request, locals }) => {
		const token = requireToken(locals.token);
		const formData = await request.formData();
		const title = String(formData.get('title') ?? '').trim();
		const description = String(formData.get('description') ?? '').trim();
		const values = { title, description };
		if (!title) return fail(400, { error: 'Informe um título para a tarefa.', values });
		if (title.length > 255) return fail(400, { error: 'O título pode ter no máximo 255 caracteres.', values });
		try {
			const response = await backendFetch('/api/v1/tasks', token, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ title, description: description || null }) });
			if (!response.ok) return fail(response.status, { error: await backendError(response), values });
		} catch { return fail(503, { error: 'Não foi possível conectar ao serviço de tarefas. Tente novamente.', values }); }
		return { message: 'Tarefa adicionada ao quadro.' };
	},
	toggle: async ({ request, locals }) => {
		const token = requireToken(locals.token);
		const formData = await request.formData();
		const id = String(formData.get('id') ?? '');
		const completed = formData.get('completed') === 'true';
		if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id)) return fail(400, { error: 'A tarefa selecionada é inválida.' });
		try {
			const response = await backendFetch(`/api/v1/tasks/${id}`, token, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ completed }) });
			if (!response.ok) return fail(response.status, { error: await backendError(response) });
		} catch { return fail(503, { error: 'Não foi possível atualizar a tarefa. Tente novamente.' }); }
		return { message: completed ? 'Tarefa concluída.' : 'Tarefa reaberta.' };
	}
};
