<script lang="ts">
	import type { PageData } from './$types';

	type Priority = 'low' | 'medium' | 'high' | 'urgent';

	let { data }: { data: PageData } = $props();

	const priorityLabels: Record<Priority, string> = {
		low: 'Baixa',
		medium: 'Média',
		high: 'Alta',
		urgent: 'Urgente'
	};

	let board = $derived(data.board);
	let columns = $derived(board?.columns ?? []);
	let totalTaskCount = $derived(columns.reduce((total, column) => total + column.tasks.length, 0));
	let completedTaskCount = $derived(
		columns.find((column) => column.name.toLocaleLowerCase().includes('conclu'))?.tasks.length ?? 0
	);
	let progress = $derived(
		totalTaskCount ? Math.round((completedTaskCount / totalTaskCount) * 100) : 0
	);

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
</script>

<svelte:head>
	<title>{board ? board.title : 'Kanban'} | UniLaunch</title>
	<meta name="description" content="Quadro Kanban da UniLaunch." />
</svelte:head>

<main class="kanban-page">
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
					<section class="kanban-column" aria-labelledby={`${column.id}-heading`}>
						<header class="column-heading">
							<div class="heading-name">
								<i></i>
								<h2 id={`${column.id}-heading`}>{column.name}</h2>
								<span>{column.tasks.length}</span>
							</div>
						</header>

						<div class="column-body">
							{#each column.tasks as task (task.id)}
								<article class="task-card">
									<h3>{task.title}</h3>
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

<style>
	:global(body) {
		overflow-x: hidden;
	}

	.kanban-page {
		min-height: calc(100vh - 4.5rem);
		background: var(--background);
		color: var(--foreground);
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
	}

	.task-card h3 {
		margin: 0 0 0.44rem;
		color: #fff;
		font: 700 0.94rem var(--app-font-display);
		letter-spacing: -0.035em;
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
	}
</style>
