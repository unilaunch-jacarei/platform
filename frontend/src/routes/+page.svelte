<script lang="ts">
	import { enhance } from '$app/forms';
	import type { SubmitFunction } from '@sveltejs/kit';
	import { tick } from 'svelte';
	import type { ActionData, PageData } from './$types';

	type Priority = 'low' | 'medium' | 'high' | 'urgent';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	const priorityLabels: Record<Priority, string> = {
		low: 'Baixa',
		medium: 'Média',
		high: 'Alta',
		urgent: 'Urgente'
	};

	const priorityOptions: { value: Priority; label: string }[] = [
		{ value: 'low', label: 'Baixa' },
		{ value: 'medium', label: 'Média' },
		{ value: 'high', label: 'Alta' },
		{ value: 'urgent', label: 'Urgente' }
	];

	let board = $derived(data.board);
	let columns = $derived(board?.columns ?? []);
	let totalTaskCount = $derived(columns.reduce((total, column) => total + column.tasks.length, 0));
	let completedTaskCount = $derived(
		columns.find((column) => column.name.toLocaleLowerCase().includes('conclu'))?.tasks.length ?? 0
	);
	let progress = $derived(
		totalTaskCount ? Math.round((completedTaskCount / totalTaskCount) * 100) : 0
	);

	let isModalOpen = $state(false);
	let newTaskColumn = $state('');
	let newTaskTitle = $state('');
	let newTaskDescription = $state('');
	let newTaskPriority = $state<Priority>('medium');
	let draggingTaskId = $state<string | null>(null);
	let dropTarget = $state<string | null>(null);
	let moveForm = $state<HTMLFormElement | null>(null);
	let moveTaskId = $state('');
	let moveColumnId = $state('');

	const createEnhance: SubmitFunction = () => async ({ result, update }) => {
		if (result.type === 'success') {
			closeModal();
			await update();
		}
	};

	function priorityClass(priority: Priority) {
		return priority;
	}

	function formatDueDate(value: string | null) {
		if (!value) return null;
		const parsed = new Date(value);
		return Number.isNaN(parsed.getTime())
			? null
			: parsed.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
	}

	function openModal(columnId: string) {
		newTaskColumn = columnId;
		newTaskTitle = '';
		newTaskDescription = '';
		newTaskPriority = 'medium';
		isModalOpen = true;
	}

	function closeModal() {
		isModalOpen = false;
	}

	function startDrag(event: DragEvent, taskId: string) {
		draggingTaskId = taskId;
		event.dataTransfer?.setData('text/plain', taskId);
		if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move';
	}

	function finishDrag() {
		draggingTaskId = null;
		dropTarget = null;
	}

	function allowDrop(event: DragEvent, columnId: string) {
		event.preventDefault();
		dropTarget = columnId;
	}

	async function moveTask(event: DragEvent, columnId: string) {
		event.preventDefault();
		const taskId = draggingTaskId ?? event.dataTransfer?.getData('text/plain');
		if (!taskId) {
			finishDrag();
			return;
		}

		moveTaskId = taskId;
		moveColumnId = columnId;
		finishDrag();
		await tick();
		moveForm?.requestSubmit();
	}
</script>

<svelte:head>
	<title>{board ? board.title : 'Kanban'} | UniLaunch</title>
	<meta name="description" content="Quadro Kanban da UniLaunch." />
</svelte:head>

<main class="kanban-page">
	<form
		method="POST"
		action="?/move"
		use:enhance
		bind:this={moveForm}
		class="hidden-form"
		aria-hidden="true"
		tabindex="-1"
	>
		<input type="hidden" name="task_id" value={moveTaskId} />
		<input type="hidden" name="column_id" value={moveColumnId} />
	</form>

	{#if form?.error}
		<p class="alert" role="alert">{form.error}</p>
	{:else if form?.message}
		<p class="notice" role="status">{form.message}</p>
	{/if}

	{#if board}
		<section class="project-overview" aria-labelledby="project-title">
			<nav aria-label="Caminho do projeto" class="breadcrumb">
				<span>‹</span> Projetos <b>/</b> <strong>{board.title}</strong>
			</nav>
			<div class="project-details">
				<div class="project-icon" aria-hidden="true">⌘</div>
				<div>
					<h1 id="project-title">{board.title}</h1>
					<p>{board.description ?? 'Quadro de tarefas'}</p>
				</div>
			</div>
			<div class="project-progress" aria-label={`Progresso do projeto: ${progress}%`}>
				<div class="progress"><i style={`width: ${progress}%`}></i></div>
				<strong>{progress}%</strong>
			</div>
		</section>

		<section class="board-scroll" aria-label="Quadro Kanban">
			<div
				class="board"
				style={`grid-template-columns: repeat(${Math.max(columns.length, 1)}, minmax(15rem, 1fr));`}
			>
				{#each columns as column (column.id)}
					<section
						class:drop-active={dropTarget === column.id && draggingTaskId !== null}
						class="kanban-column"
						ondragover={(event) => allowDrop(event, column.id)}
						ondragleave={() => (dropTarget = null)}
						ondrop={(event) => moveTask(event, column.id)}
						aria-labelledby={`${column.id}-heading`}
					>
						<header class="column-heading">
							<div class="heading-name">
								<i></i>
								<h2 id={`${column.id}-heading`}>{column.name}</h2>
								<span>{column.tasks.length}</span>
							</div>
							<button
								class="add-card"
								type="button"
								aria-label={`Adicionar tarefa em ${column.name}`}
								onclick={() => openModal(column.id)}
							>
								+
							</button>
						</header>

						<div class="column-body">
							{#each column.tasks as task (task.id)}
								<article
									class:dragging={draggingTaskId === task.id}
									class="task-card"
									draggable="true"
									ondragstart={(event) => startDrag(event, task.id)}
									ondragend={finishDrag}
								>
									<header class="task-header">
										<h3>{task.title}</h3>
										<form method="POST" action="?/delete" use:enhance class="task-delete">
											<input type="hidden" name="task_id" value={task.id} />
											<button type="submit" aria-label={`Excluir ${task.title}`} title="Excluir">
												×
											</button>
										</form>
									</header>
									{#if task.description}
										<p class="task-description">{task.description}</p>
									{/if}
									<div class="task-meta">
										<span class={`priority ${priorityClass(task.priority)}`}>
											⚑ {priorityLabels[task.priority]}
										</span>
										{#if formatDueDate(task.due_date)}
											<span>◷ {formatDueDate(task.due_date)}</span>
										{/if}
									</div>
								</article>
							{:else}
								<p class="column-empty">Nenhuma tarefa.</p>
							{/each}
						</div>
					</section>
				{:else}
					<p class="column-empty">Este quadro ainda não possui colunas.</p>
				{/each}
			</div>
		</section>
	{:else}
		<section class="empty-state">
			<h1>Nenhum quadro por aqui</h1>
			<p>
				{data.unavailable
					? 'Não foi possível carregar seus quadros agora. Tente novamente em instantes.'
					: 'Você ainda não participa de nenhum quadro.'}
			</p>
		</section>
	{/if}
</main>

{#if isModalOpen}
	<button class="modal-backdrop" type="button" aria-label="Fechar nova tarefa" onclick={closeModal}
	></button>
	<dialog open class="task-modal" aria-labelledby="modal-title">
		<form method="POST" action="?/create" use:enhance={createEnhance} class="task-form">
			<input type="hidden" name="column_id" value={newTaskColumn} />
			<header>
				<h2 id="modal-title">Nova tarefa</h2>
				<button type="button" aria-label="Fechar" onclick={closeModal}>×</button>
			</header>
			<label class="field full">
				<span>Título <b>*</b></span>
				<input
					name="title"
					bind:value={newTaskTitle}
					placeholder="Nome da tarefa"
					maxlength="255"
					required
				/>
			</label>
			<label class="field full">
				<span>Descrição</span>
				<textarea
					name="description"
					bind:value={newTaskDescription}
					rows="3"
					placeholder="Descreva a tarefa..."
				></textarea>
			</label>
			<label class="field full">
				<span>Prioridade</span>
				<select name="priority" bind:value={newTaskPriority}>
					{#each priorityOptions as option (option.value)}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</label>
			{#if form?.error}
				<p class="form-error" role="alert">{form.error}</p>
			{/if}
			<footer>
				<button class="cancel" type="button" onclick={closeModal}>Cancelar</button>
				<button class="create" type="submit">Criar tarefa</button>
			</footer>
		</form>
	</dialog>
{/if}

<style>
	:global(body) {
		overflow-x: hidden;
	}

	.hidden-form {
		display: none;
	}

	.kanban-page {
		min-height: calc(100vh - 4.5rem);
		background: var(--background);
		color: var(--foreground);
	}

	.alert,
	.notice {
		margin: 0;
		padding: 0.7rem 1.85rem;
		font-size: 0.85rem;
	}

	.alert {
		background: #3a1220;
		color: #ffb3c0;
	}

	.notice {
		background: #102a24;
		color: #8fe3c8;
	}

	.project-overview {
		position: relative;
		min-height: 8.7rem;
		box-sizing: border-box;
		padding: 1.35rem 1.85rem 1.25rem;
		border-bottom: 1px solid var(--border);
		background: #0d1026;
	}

	.breadcrumb {
		display: flex;
		align-items: center;
		gap: 0.55rem;
		color: #6f83a4;
		font-size: 0.96rem;
		font-weight: 500;
	}

	.breadcrumb span {
		font-size: 1.45rem;
		line-height: 0.6;
	}

	.breadcrumb b {
		color: #536078;
	}

	.breadcrumb strong {
		color: var(--foreground);
	}

	.project-details {
		display: flex;
		gap: 0.9rem;
		align-items: center;
		margin-top: 1.1rem;
	}

	.project-icon {
		display: grid;
		width: 2.8rem;
		height: 2.8rem;
		place-items: center;
		border: 1px solid #3d3577;
		border-radius: 50%;
		background: #201e4a;
		color: #d6e95d;
		font-size: 1.65rem;
		font-weight: 800;
		transform: rotate(-14deg);
	}

	.project-details h1 {
		margin: 0 0 0.15rem;
		font: 800 1.15rem var(--app-font-display);
		letter-spacing: -0.04em;
	}

	.project-details p {
		margin: 0;
		color: #7085a7;
		font-size: 0.77rem;
	}

	.project-progress {
		position: absolute;
		right: 1.85rem;
		bottom: 2.25rem;
		display: flex;
		align-items: center;
		gap: 0.65rem;
	}

	.progress {
		width: 7.5rem;
		height: 0.42rem;
		overflow: hidden;
		border-radius: 1rem;
		background: #202744;
	}

	.progress i {
		display: block;
		height: 100%;
		border-radius: inherit;
		background: #7859ff;
		transition: width 0.2s ease;
	}

	.project-progress > strong {
		color: #9073ff;
		font-size: 0.9rem;
	}

	.board-scroll {
		overflow-x: auto;
		padding: 1.9rem 1.85rem;
	}

	.board {
		display: grid;
		gap: 1.25rem;
	}

	.kanban-column {
		min-height: 43.8rem;
		border: 1px solid #302766;
		border-radius: 1.15rem;
		background: rgba(10, 13, 32, 0.62);
		transition: border-color 0.18s, background 0.18s;
	}

	.kanban-column.drop-active {
		border-color: #7859ff;
		background: rgba(120, 89, 255, 0.12);
		box-shadow: inset 0 0 0 1px #7859ff;
	}

	.column-heading {
		display: flex;
		align-items: center;
		justify-content: space-between;
		min-height: 2.75rem;
		padding: 0.72rem 0.82rem 0.45rem;
	}

	.heading-name {
		display: flex;
		align-items: center;
		gap: 0.58rem;
	}

	.heading-name i {
		width: 0.64rem;
		height: 0.64rem;
		border-radius: 50%;
		background: #7064ff;
	}

	.heading-name h2 {
		margin: 0;
		color: #fff;
		font: 800 0.98rem var(--app-font-display);
		letter-spacing: -0.02em;
	}

	.heading-name span {
		display: grid;
		width: 1.48rem;
		height: 1.48rem;
		place-items: center;
		border-radius: 50%;
		background: #1b2344;
		color: #72809e;
		font-size: 0.73rem;
	}

	.add-card {
		display: grid;
		width: 2rem;
		height: 2rem;
		place-items: center;
		border: 0;
		border-radius: 50%;
		padding: 0;
		background: transparent;
		color: #71809d;
		cursor: pointer;
		font-size: 1.3rem;
		line-height: 1;
	}

	.add-card:hover {
		color: #fff;
		background: #1b2344;
	}

	.column-body {
		display: grid;
		gap: 0.65rem;
		padding: 0.65rem;
	}

	.task-card {
		display: flex;
		min-height: 6rem;
		box-sizing: border-box;
		flex-direction: column;
		padding: 1.05rem;
		border: 1px solid #302766;
		border-radius: 1.12rem;
		background: #1d2342;
		box-shadow: 0 10px 20px rgba(0, 0, 0, 0.07);
		cursor: grab;
		transition: opacity 0.15s, transform 0.15s;
	}

	.task-card.dragging {
		opacity: 0.28;
	}

	.task-card:active {
		cursor: grabbing;
		transform: rotate(1deg);
	}

	.task-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 0.5rem;
	}

	.task-header h3 {
		margin: 0 0 0.44rem;
		color: #fff;
		font: 700 0.94rem var(--app-font-display);
		letter-spacing: -0.035em;
	}

	.task-delete button {
		border: 0;
		padding: 0;
		background: transparent;
		color: #71809d;
		cursor: pointer;
		font-size: 1.1rem;
		line-height: 1;
	}

	.task-delete button:hover {
		color: #ff7b8a;
	}

	.task-description {
		margin: 0 0 0.4rem;
		color: #8c9ab6;
		font-size: 0.72rem;
	}

	.task-meta {
		display: flex;
		gap: 0.68rem;
		align-items: center;
		margin-top: auto;
		color: #71809d;
		font-size: 0.72rem;
	}

	.priority {
		font-weight: 700;
	}

	.priority.low {
		color: #21c99b;
	}

	.priority.medium {
		color: #f3af1d;
	}

	.priority.high {
		color: #fa535d;
	}

	.priority.urgent {
		color: #ff7ad9;
	}

	.column-empty {
		margin: 0;
		padding: 0.75rem;
		color: #71809d;
		font-size: 0.8rem;
	}

	.empty-state {
		display: grid;
		min-height: calc(100vh - 4.5rem);
		place-content: center;
		gap: 0.5rem;
		padding: 2rem;
		text-align: center;
	}

	.empty-state h1 {
		margin: 0;
		font: 800 1.3rem var(--app-font-display);
	}

	.empty-state p {
		margin: 0;
		color: #71809d;
	}

	.modal-backdrop {
		position: fixed;
		z-index: 20;
		inset: 0;
		border: 0;
		background: rgba(0, 2, 12, 0.78);
		backdrop-filter: blur(6px);
		cursor: default;
	}

	.task-modal {
		position: fixed;
		z-index: 21;
		top: 50%;
		left: 50%;
		width: min(38rem, calc(100vw - 2rem));
		max-height: calc(100dvh - 2rem);
		box-sizing: border-box;
		overflow-y: auto;
		transform: translate(-50%, -50%);
		border: 1px solid #332777;
		border-radius: 1.15rem;
		padding: 1.85rem;
		background: #10142d;
		color: var(--foreground);
		box-shadow: 0 24px 70px rgba(0, 0, 0, 0.6);
	}

	.task-modal header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1.35rem;
	}

	.task-modal h2 {
		margin: 0;
		font: 800 1.18rem var(--app-font-display);
		letter-spacing: -0.04em;
	}

	.task-modal header button {
		display: grid;
		width: 2rem;
		height: 2rem;
		place-items: center;
		border: 0;
		padding: 0;
		background: transparent;
		color: #71809d;
		cursor: pointer;
		font-size: 1.55rem;
		line-height: 1;
	}

	.field {
		display: grid;
		gap: 0.5rem;
		color: #f3f4fb;
		font-size: 0.78rem;
		font-weight: 700;
	}

	.field.full {
		margin-bottom: 1.15rem;
	}

	.field b {
		color: #ff5b68;
	}

	.field input,
	.field textarea,
	.field select {
		width: 100%;
		box-sizing: border-box;
		border: 1px solid #2b2660;
		border-radius: 0.95rem;
		padding: 0.72rem 0.92rem;
		background: #161d30;
		color: var(--foreground);
		font: 500 0.9rem var(--app-font-display);
		outline: none;
	}

	.field textarea {
		resize: vertical;
	}

	.form-error {
		margin: 0 0 1rem;
		color: #ff7b8a;
		font-size: 0.82rem;
	}

	.task-form footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.65rem;
	}

	.task-form footer button {
		border: 0;
		border-radius: 0.9rem;
		padding: 0.65rem 1.1rem;
		cursor: pointer;
		font: 700 0.85rem var(--app-font-display);
	}

	.task-form .cancel {
		background: #1b2344;
		color: #c3cbe0;
	}

	.task-form .create {
		background: #7859ff;
		color: #fff;
	}

	@media (max-width: 780px) {
		.project-overview {
			min-height: 13rem;
			padding: 1.15rem;
		}

		.project-progress {
			right: 1.15rem;
			bottom: 1.2rem;
		}

		.progress {
			width: 4rem;
		}

		.board-scroll {
			padding: 1.75rem 1.15rem;
		}

		.task-modal {
			padding: 1.3rem;
		}
	}
</style>
