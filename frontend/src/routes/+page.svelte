<script lang="ts">
	import type { PageData } from './$types';

	type TagTone = 'cyan' | 'purple' | 'green' | 'yellow' | 'pink' | 'rose';
	type Priority = 'Alta' | 'Média' | 'Baixa';
	type BoardTask = {
		id: string;
		title: string;
		description?: string | null;
		tags: { label: string; tone: TagTone }[];
		technology: string;
		priority: Priority;
		deadline: string;
		assignee: string;
		comments: number;
		attachments: number;
	};
	type BoardColumn = {
		id: string;
		title: string;
		color: string;
		tasks: BoardTask[];
	};

	let { data }: { data: PageData } = $props();

	const columnsMeta = [
		{ id: 'backlog', title: 'Backlog', color: '#73829e' },
		{ id: 'todo', title: 'A Fazer', color: '#7064ff' },
		{ id: 'progress', title: 'Em Andamento', color: '#8a3ffc' },
		{ id: 'review', title: 'Em Revisão', color: '#f6a719' },
		{ id: 'done', title: 'Concluído', color: '#19d49c' }
	] as const;

	const demoColumns: BoardColumn[] = [
		{
			...columnsMeta[0],
			tasks: [
				{ id: 'demo-1', title: 'Setup CI/CD pipeline', tags: [{ label: 'DevOps', tone: 'cyan' }], technology: 'Docker', priority: 'Baixa', deadline: '20/07', assignee: 'L', comments: 2, attachments: 0 },
				{ id: 'demo-2', title: 'Documentação da API', tags: [{ label: 'Documentação', tone: 'purple' }, { label: 'API', tone: 'purple' }], technology: 'Node.js', priority: 'Média', deadline: '25/07', assignee: 'L', comments: 0, attachments: 1 }
			]
		},
		{
			...columnsMeta[1],
			tasks: [
				{ id: 'demo-3', title: 'Tela de dashboard v2', tags: [{ label: 'Front-end', tone: 'purple' }, { label: 'UI', tone: 'green' }], technology: 'React', priority: 'Alta', deadline: '18/07', assignee: 'M', comments: 5, attachments: 2 },
				{ id: 'demo-4', title: 'Integração Stripe', tags: [{ label: 'Back-end', tone: 'green' }, { label: 'API', tone: 'purple' }], technology: 'Node.js', priority: 'Alta', deadline: '19/07', assignee: 'E', comments: 3, attachments: 1 }
			]
		},
		{
			...columnsMeta[2],
			tasks: [
				{ id: 'demo-5', title: 'Refatorar autenticação', tags: [{ label: 'Auth', tone: 'yellow' }, { label: 'Back-end', tone: 'green' }], technology: 'Node.js', priority: 'Alta', deadline: '15/07', assignee: 'M', comments: 8, attachments: 3 },
				{ id: 'demo-6', title: 'Testes unitários', tags: [{ label: 'QA', tone: 'yellow' }], technology: 'TypeScript', priority: 'Média', deadline: '16/07', assignee: 'L', comments: 2, attachments: 0 }
			]
		},
		{
			...columnsMeta[3],
			tasks: [
				{ id: 'demo-7', title: 'Busca com filtros', tags: [{ label: 'Front-end', tone: 'purple' }, { label: 'UI', tone: 'green' }], technology: 'React', priority: 'Média', deadline: '12/07', assignee: 'L', comments: 4, attachments: 1 }
			]
		},
		{
			...columnsMeta[4],
			tasks: [
				{ id: 'demo-8', title: 'Setup do projeto', tags: [{ label: 'DevOps', tone: 'cyan' }], technology: 'Git', priority: 'Alta', deadline: '01/07', assignee: 'A', comments: 1, attachments: 0 }
			]
		}
	];

	const availableTags: { label: string; tone: TagTone }[] = [
		{ label: 'Front-end', tone: 'purple' }, { label: 'Back-end', tone: 'green' },
		{ label: 'Design', tone: 'pink' }, { label: 'QA', tone: 'yellow' },
		{ label: 'DevOps', tone: 'cyan' }, { label: 'Urgente', tone: 'rose' },
		{ label: 'Documentação', tone: 'purple' }, { label: 'API', tone: 'purple' },
		{ label: 'Auth', tone: 'yellow' }, { label: 'UI', tone: 'green' }
	];

	function cloneDemo(): BoardColumn[] {
		return demoColumns.map((column) => ({ ...column, tasks: column.tasks.map((task) => ({ ...task, tags: [...task.tags] })) }));
	}

	function createInitialColumns(): BoardColumn[] {
		if (data.unavailable) return cloneDemo();

		const fromServer = (task: PageData['tasks'][number]): BoardTask => ({
			id: task.id,
			title: task.title,
			description: task.description,
			tags: [],
			technology: 'Task',
			priority: 'Média',
			deadline: 'Hoje',
			assignee: 'L',
			comments: 0,
			attachments: 0
		});

		return columnsMeta.map((column) => ({
			...column,
			tasks: column.id === 'todo' ? data.pendingTasks.map(fromServer) : column.id === 'done' ? data.completedTasks.map(fromServer) : []
		}));
	}

	let columns = $state<BoardColumn[]>(createInitialColumns());
	let draggingTaskId = $state<string | null>(null);
	let dropTarget = $state<string | null>(null);
	let isModalOpen = $state(false);
	let newTaskColumn = $state('todo');
	let newTaskTitle = $state('');
	let newTaskDescription = $state('');
	let newTaskAssignee = $state('');
	let newTaskDeadline = $state('');
	let newTaskPriority = $state<Priority>('Média');
	let newTaskTechnology = $state('');
	let newTaskTags = $state<{ label: string; tone: TagTone }[]>([]);
	let newTagInput = $state('');
	let tagInputElement = $state<HTMLInputElement | null>(null);
	let totalTaskCount = $derived(columns.reduce((total, column) => total + column.tasks.length, 0));
	let completedTaskCount = $derived(columns.find((column) => column.id === 'done')?.tasks.length ?? 0);
	let progress = $derived(totalTaskCount ? Math.round((completedTaskCount / totalTaskCount) * 100) : 0);
	let suggestedTags = $derived(availableTags.filter((tag) => tag.label.toLocaleLowerCase().includes(newTagInput.trim().toLocaleLowerCase()) && !newTaskTags.some((selectedTag) => selectedTag.label === tag.label)));

	function openModal(columnId: string) {
		newTaskColumn = columnId;
		newTaskTitle = '';
		newTaskDescription = '';
		newTaskAssignee = '';
		newTaskDeadline = '';
		newTaskPriority = 'Média';
		newTaskTechnology = '';
		newTaskTags = [];
		newTagInput = '';
		isModalOpen = true;
	}

	function closeModal() {
		isModalOpen = false;
	}

	function addTag(label: string, tone: TagTone) {
		if (newTaskTags.some((tag) => tag.label === label)) return;
		newTaskTags = [...newTaskTags, { label, tone }];
	}

	function removeTag(label: string) {
		newTaskTags = newTaskTags.filter((tag) => tag.label !== label);
	}

	function toggleTag(tag: { label: string; tone: TagTone }) {
		if (newTaskTags.some((selectedTag) => selectedTag.label === tag.label)) removeTag(tag.label);
		else addTag(tag.label, tag.tone);
	}

	function addTypedTag() {
		const label = newTagInput.trim();
		if (!label) {
			tagInputElement?.focus();
			return;
		}
		const matchingTag = availableTags.find((tag) => tag.label.toLocaleLowerCase() === label.toLocaleLowerCase());
		addTag(matchingTag?.label ?? label, matchingTag?.tone ?? 'purple');
		newTagInput = '';
		tagInputElement?.focus();
	}

	function handleTagKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			event.preventDefault();
			addTypedTag();
		}
		if (event.key === 'Backspace' && !newTagInput && newTaskTags.length) removeTag(newTaskTags.at(-1)?.label ?? '');
	}

	function createTask() {
		const title = newTaskTitle.trim();
		if (!title) return;

		const newTask: BoardTask = {
			id: `local-${Date.now()}`,
			title,
			description: newTaskDescription.trim() || undefined,
			tags: newTaskTags,
			technology: newTaskTechnology.trim() || 'Task',
			priority: newTaskPriority,
			deadline: newTaskDeadline.trim() || 'Sem prazo',
			assignee: (newTaskAssignee.trim() || 'L').slice(0, 1).toUpperCase(),
			comments: 0,
			attachments: 0
		};

		columns = columns.map((column) => column.id === newTaskColumn ? { ...column, tasks: [...column.tasks, newTask] } : column);
		closeModal();
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

	function moveTask(event: DragEvent, destinationId: string) {
		event.preventDefault();
		const taskId = draggingTaskId ?? event.dataTransfer?.getData('text/plain');
		if (!taskId) return finishDrag();

		let movedTask: BoardTask | undefined;
		const withoutTask = columns.map((column) => ({
			...column,
			tasks: column.tasks.filter((task) => {
				if (task.id === taskId) movedTask = task;
				return task.id !== taskId;
			})
		}));

		columns = withoutTask.map((column) => column.id === destinationId && movedTask ? { ...column, tasks: [...column.tasks, movedTask] } : column);
		finishDrag();
	}

	function deleteTask(event: DragEvent) {
		event.preventDefault();
		const taskId = draggingTaskId ?? event.dataTransfer?.getData('text/plain');
		if (taskId) columns = columns.map((column) => ({ ...column, tasks: column.tasks.filter((task) => task.id !== taskId) }));
		finishDrag();
	}

	function priorityClass(priority: Priority) {
		return priority === 'Alta' ? 'high' : priority === 'Média' ? 'medium' : 'low';
	}
</script>

<svelte:head>
	<title>Kanban | UniLaunch</title>
	<meta name="description" content="Quadro Kanban do projeto App Financeiro na UniLaunch." />
</svelte:head>

<main class="kanban-page">
	<section class="project-overview" aria-labelledby="project-title">
		<nav aria-label="Caminho do projeto" class="breadcrumb"><span>‹</span> Projetos <b>/</b> <strong>App Financeiro</strong></nav>
		<div class="project-details">
			<div class="project-icon" aria-hidden="true">⌘</div>
			<div>
				<h1 id="project-title">App Financeiro</h1>
				<p>Engenharia de Software</p>
			</div>
		</div>
		<div class="project-progress" aria-label={`Progresso do projeto: ${progress}%`}>
			<div class="project-tags"><span>React Native</span><span>Node.js</span><span>PostgreSQL</span></div>
			<div class="progress"><i style={`width: ${progress}%`}></i></div><strong>{progress}%</strong>
		</div>
	</section>

	<section class="board-scroll" aria-label="Quadro Kanban">
		<div class="board">
			{#each columns as column (column.id)}
				<section
					class:drop-active={dropTarget === column.id && draggingTaskId !== null}
					class="kanban-column"
					style={`--column-color: ${column.color}`}
					ondragover={(event) => allowDrop(event, column.id)}
					ondragleave={() => dropTarget = null}
					ondrop={(event) => moveTask(event, column.id)}
					aria-labelledby={`${column.id}-heading`}
				>
					<header class="column-heading">
						<div class="heading-name">
							<i style={`background:${column.color}`}></i>
							<h2 id={`${column.id}-heading`}>{column.title}</h2>
							<span>{column.tasks.length}</span>
						</div>
						<button class="add-card" type="button" aria-label={`Adicionar tarefa em ${column.title}`} onclick={() => openModal(column.id)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg></button>
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
								<div class="task-tags">
									{#each task.tags as tag}
										<span class={`tag ${tag.tone}`}>{tag.label}</span>
									{/each}
								</div>
								<h3>{task.title}</h3>
								{#if task.description}<p class="task-description">{task.description}</p>{/if}
								<span class="technology">⌁ {task.technology}</span>
								<div class="task-meta"><span class={`priority ${priorityClass(task.priority)}`}>⚑ {task.priority}</span><span>◷ {task.deadline}</span></div>
								<footer>
									<span class="assignee" aria-label={`Responsável: ${task.assignee}`}>{task.assignee}</span>
									<div class="task-counts">
										{#if task.comments}<span title="Comentários">▱ {task.comments}</span>{/if}
										{#if task.attachments}<span title="Anexos">♧ {task.attachments}</span>{/if}
									</div>
								</footer>
							</article>
						{/each}
					</div>
				</section>
			{/each}
		</div>
	</section>

	{#if draggingTaskId}
		<div class="delete-dropzone" role="presentation" ondragover={(event) => event.preventDefault()} ondrop={deleteTask}>⌫ <strong>Arraste aqui para excluir</strong></div>
	{/if}
</main>

{#if isModalOpen}
	<button class="modal-backdrop" type="button" aria-label="Fechar nova task" onclick={closeModal}></button>
	<dialog open class="task-modal" aria-labelledby="modal-title">
		<header><h2 id="modal-title">Nova task</h2><button type="button" aria-label="Fechar" onclick={closeModal}>×</button></header>
		<label class="field full"><span>Título <b>*</b></span><input bind:value={newTaskTitle} placeholder="Nome da task" maxlength="255" /></label>
		<label class="field full"><span>Descrição</span><textarea bind:value={newTaskDescription} rows="3" placeholder="Descreva a task..."></textarea></label>
		<div class="field-grid">
			<label class="field"><span>Responsável</span><input bind:value={newTaskAssignee} placeholder="Nome" /></label>
			<label class="field"><span>Prazo</span><input bind:value={newTaskDeadline} placeholder="dd/mm" /></label>
			<label class="field"><span>Prioridade</span><select bind:value={newTaskPriority}><option>Baixa</option><option>Média</option><option>Alta</option></select></label>
			<label class="field"><span>Tecnologia</span><input bind:value={newTaskTechnology} placeholder="⌁  React, Node.js..." /></label>
		</div>
		<div class="tags-field"><span>Tags</span><div class="tag-composer"><div class="tag-input"><span aria-hidden="true">◇</span>{#each newTaskTags as tag (tag.label)}<span class={`selected-tag ${tag.tone}`}>{tag.label}<button type="button" aria-label={`Remover ${tag.label}`} onclick={() => removeTag(tag.label)}>×</button></span>{/each}<input bind:this={tagInputElement} bind:value={newTagInput} onkeydown={handleTagKeydown} placeholder={newTaskTags.length ? 'Adicionar tag...' : 'Nova tag...'} /><button class="add-tag" type="button" aria-label="Adicionar tag" onclick={addTypedTag}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg></button></div>{#if newTagInput.trim()}<div class="tag-suggestions">{#each suggestedTags as tag}<button type="button" onmousedown={(event) => event.preventDefault()} onclick={() => { addTag(tag.label, tag.tone); newTagInput = ''; tagInputElement?.focus(); }}>{tag.label}</button>{:else}<span>Nenhuma tag encontrada. Pressione Enter para criar “{newTagInput.trim()}”.</span>{/each}</div>{/if}</div><div class="tag-options">
			{#each availableTags as tag}
				<button class={`tag ${tag.tone}`} class:selected={newTaskTags.some((selectedTag) => selectedTag.label === tag.label)} type="button" onclick={() => toggleTag(tag)}>{tag.label}</button>
			{/each}
		</div></div>
		<footer><button class="cancel" type="button" onclick={closeModal}>Cancelar</button><button class="create" type="button" onclick={createTask}>Criar task</button></footer>
	</dialog>
{/if}

<style>
	:global(body) { overflow-x: hidden; }
	.kanban-page { min-height: calc(100vh - 4.5rem); background: var(--background); color: var(--foreground); }
	.project-overview { position: relative; min-height: 8.7rem; box-sizing: border-box; padding: 1.35rem 1.85rem 1.25rem; border-bottom: 1px solid var(--border); background: #0d1026; }
	.breadcrumb { display: flex; align-items: center; gap: .55rem; color: #6f83a4; font-size: .96rem; font-weight: 500; }.breadcrumb span { font-size: 1.45rem; line-height: .6; }.breadcrumb b { color: #536078; }.breadcrumb strong { color: var(--foreground); }
	.project-details { display: flex; gap: .9rem; align-items: center; margin-top: 1.1rem; }.project-icon { display: grid; width: 2.8rem; height: 2.8rem; place-items: center; border: 1px solid #3d3577; border-radius: 50%; background: #201e4a; color: #d6e95d; font-size: 1.65rem; font-weight: 800; transform: rotate(-14deg); }.project-details h1 { margin: 0 0 .15rem; font: 800 1.15rem var(--app-font-display); letter-spacing: -.04em; }.project-details p { margin: 0; color: #7085a7; font-size: .77rem; }
	.project-progress { position: absolute; right: 1.85rem; bottom: 2.25rem; display: flex; align-items: center; gap: .65rem; }.project-tags { display: flex; gap: .45rem; }.project-tags span { padding: .28rem .62rem; border: 1px solid #372278; border-radius: 999px; background: #180e42; color: #a77bff; font: 500 .72rem var(--app-font-mono); }.progress { width: 7.5rem; height: .42rem; overflow: hidden; border-radius: 1rem; background: #202744; }.progress i { display: block; height: 100%; border-radius: inherit; background: #7859ff; transition: width .2s ease; }.project-progress > strong { color: #9073ff; font-size: .9rem; }
	.board-scroll { overflow-x: auto; padding: 1.9rem 1.85rem 1.9rem; }.board { display: grid; min-width: 96rem; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 1.25rem; }
	.kanban-column { min-height: 43.8rem; border: 1px solid var(--column-color); border-radius: 1.15rem; background: rgba(10, 13, 32, .62); transition: border-color .18s, background .18s; }.kanban-column.drop-active { border-color: var(--column-color); background: color-mix(in srgb, var(--column-color) 12%, rgba(10, 13, 32, .88)); box-shadow: inset 0 0 0 1px var(--column-color); }
	.column-heading { display: flex; align-items: center; justify-content: space-between; min-height: 2.75rem; padding: .72rem .82rem .45rem; }.heading-name { display: flex; align-items: center; gap: .58rem; }.heading-name i { width: .64rem; height: .64rem; border-radius: 50%; }.heading-name h2 { margin: 0; color: #fff; font: 800 .98rem var(--app-font-display); letter-spacing: -.02em; }.heading-name span { display: grid; width: 1.48rem; height: 1.48rem; place-items: center; border-radius: 50%; background: #1b2344; color: #72809e; font-size: .73rem; }.add-card { display: grid; width: 2rem; height: 2rem; place-items: center; border: 0; border-radius: 50%; padding: 0; background: transparent; color: #71809d; cursor: pointer; transform: none; }.add-card svg, .add-tag svg { display: block; width: 1.05rem; height: 1.05rem; overflow: visible; }.add-card svg path, .add-tag svg path { fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; }
	.column-body { display: grid; gap: .65rem; padding: .65rem; }.task-card { display: flex; min-height: 10.2rem; box-sizing: border-box; flex-direction: column; padding: 1.05rem; border: 1px solid #302766; border-radius: 1.12rem; background: #1d2342; box-shadow: 0 10px 20px rgba(0,0,0,.07); cursor: grab; transition: opacity .15s, transform .15s; }.task-card.dragging { opacity: .28; }.task-card:active { cursor: grabbing; transform: rotate(1deg); }.task-tags { display: flex; min-height: 1.55rem; flex-wrap: wrap; gap: .3rem; }.tag { display: inline-flex; align-items: center; width: max-content; max-width: 100%; box-sizing: border-box; border: 1px solid transparent; border-radius: 999px; padding: .2rem .52rem; font-size: .71rem; font-weight: 600; line-height: 1; }.tag.cyan { background: #0c3f5d; border-color: #17698d; color: #22d6fc; }.tag.purple { background: #30265d; border-color: #5141a0; color: #a386ff; }.tag.green { background: #123f42; border-color: #246767; color: #16d4a2; }.tag.yellow { background: #45361d; border-color: #725b31; color: #f2cd58; }.tag.pink { background: #4a224e; border-color: #75326c; color: #f473c0; }.tag.rose { background: #552b3a; border-color: #7b3c50; color: #fb9ea4; }.task-card h3 { margin: .65rem 0 .44rem; color: #fff; font: 700 .94rem var(--app-font-display); letter-spacing: -.035em; }.task-description { margin: -.2rem 0 .4rem; color: #8c9ab6; font-size: .72rem; }.technology { width: max-content; border: 1px solid #3e2980; border-radius: 999px; padding: .18rem .5rem; color: #aa8bff; background: #211451; font: .7rem var(--app-font-mono); }.task-meta { display: flex; gap: .68rem; align-items: center; margin-top: .9rem; color: #71809d; font-size: .72rem; }.priority { font-weight: 700; }.priority.high { color: #fa535d; }.priority.medium { color: #f3af1d; }.priority.low { color: #21c99b; }.task-card footer { display: flex; align-items: end; justify-content: space-between; margin-top: auto; }.assignee { display: grid; width: 1.82rem; height: 1.82rem; place-items: center; border-radius: 50%; background: #7353ed; color: white; font: 700 .7rem var(--app-font-display); }.task-counts { display: flex; gap: .45rem; color: #71809d; font-size: .7rem; }
	.delete-dropzone { position: fixed; z-index: 5; right: 50%; bottom: 1.75rem; display: flex; min-width: 17.5rem; justify-content: center; gap: .8rem; transform: translateX(50%); border: 2px solid #a52643; border-radius: 1.15rem; padding: .92rem 1.35rem; background: #0d1024; color: #ff9ca8; box-shadow: 0 12px 32px rgba(0,0,0,.42); }
	.modal-backdrop { position: fixed; z-index: 20; inset: 0; border: 0; background: rgba(0, 2, 12, .78); backdrop-filter: blur(6px); cursor: default; }.task-modal { position: fixed; z-index: 21; top: 50%; left: 50%; width: min(38rem, calc(100vw - 2rem)); max-height: calc(100dvh - 2rem); box-sizing: border-box; overflow-y: auto; transform: translate(-50%, -50%); border: 1px solid #332777; border-radius: 1.15rem; padding: 1.85rem; background: #10142d; color: var(--foreground); box-shadow: 0 24px 70px rgba(0,0,0,.6); }.task-modal header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.35rem; }.task-modal h2 { margin: 0; font: 800 1.18rem var(--app-font-display); letter-spacing: -.04em; }.task-modal header button { display: grid; width: 2rem; height: 2rem; place-items: center; border: 0; padding: 0; background: transparent; color: #71809d; cursor: pointer; font-size: 1.55rem; line-height: 1; }.field { display: grid; gap: .5rem; color: #f3f4fb; font-size: .78rem; font-weight: 700; }.field.full { margin-bottom: 1.15rem; }.field b { color: #ff5b68; }.field input, .field textarea, .field select { width: 100%; box-sizing: border-box; border: 1px solid #2b2660; border-radius: .95rem; padding: .72rem .92rem; background: #161d30; color: var(--foreground); font: 500 .9rem var(--app-font-display); outline: none; }.field textarea { resize: vertical; }.field input::placeholder, .field textarea::placeholder, .tag-input input::placeholder { color: #72809a; }.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.05rem .9rem; }.tags-field { display: grid; gap: .55rem; margin-top: 1.15rem; color: #f3f4fb; font-size: .78rem; font-weight: 700; }.tag-composer { position: relative; }.tag-input { display: flex; min-height: 3.15rem; align-items: center; flex-wrap: wrap; gap: .38rem; box-sizing: border-box; border: 1px solid #2b2660; border-radius: .95rem; padding: .38rem .4rem .38rem .85rem; background: #161d30; color: #72809a; }.tag-input input { min-width: 6rem; flex: 1; border: 0; padding: .38rem 0; background: transparent; color: var(--foreground); font: 500 .9rem var(--app-font-display); outline: none; }.selected-tag { display: inline-flex; align-items: center; gap: .28rem; border-radius: 999px; padding: .23rem .48rem; font-size: .7rem; line-height: 1; }.selected-tag.cyan { background: #0c3f5d; color: #22d6fc; }.selected-tag.purple { background: #30265d; color: #a386ff; }.selected-tag.green { background: #123f42; color: #16d4a2; }.selected-tag.yellow { background: #45361d; color: #f2cd58; }.selected-tag.pink { background: #4a224e; color: #f473c0; }.selected-tag.rose { background: #552b3a; color: #fb9ea4; }.selected-tag button { display: grid; width: .78rem; height: .78rem; flex: 0 0 .78rem; place-items: center; border: 0; margin: 0; padding: 0; background: transparent; color: inherit; cursor: pointer; font-size: 0; line-height: 0; }.selected-tag button::before { content: '×'; font: 700 .82rem/1 Arial, sans-serif; }.tag-input .add-tag { display: grid; width: 2.3rem; height: 2.3rem; place-items: center; border: 0; border-radius: 50%; padding: 0; background: #372071; color: #c5a7ff; cursor: pointer; transform: none; }.tag-suggestions { position: absolute; z-index: 3; top: calc(100% + .35rem); left: 0; width: 12rem; overflow: hidden; border: 1px solid #2b2660; border-radius: .8rem; background: #17201e; box-shadow: 0 .8rem 1.8rem rgba(0,0,0,.35); }.tag-suggestions button, .tag-suggestions span { display: block; width: 100%; box-sizing: border-box; border: 0; padding: .75rem .85rem; background: transparent; color: #e8ebf3; text-align: left; font: 700 .75rem var(--app-font-display); }.tag-suggestions button { cursor: pointer; }.tag-suggestions button:hover { background: #303b38; }.tag-suggestions span { color: #a5b0bd; font-weight: 500; }.tag-options { display: flex; flex-wrap: wrap; gap: .38rem; }.tag-options button { cursor: pointer; opacity: .88; }.tag-options button.selected { outline: 2px solid #e2d8ff; opacity: 1; }.task-modal footer { display: grid; grid-template-columns: 1fr 1fr; gap: .9rem; margin-top: 1.6rem; }.task-modal footer button { border-radius: 1rem; padding: .85rem 1rem; cursor: pointer; font: 800 .92rem var(--app-font-display); }.cancel { border: 1px solid #342875; background: #202440; color: #f4f4f8; }.create { border: 0; background: linear-gradient(110deg, #8437ed, #625ff1); color: white; }
	@media (max-width: 780px) { .project-overview { min-height: 13rem; padding: 1.15rem; }.project-progress { right: 1.15rem; bottom: 1.2rem; }.project-tags span { padding: .22rem .4rem; font-size: .6rem; }.progress { width: 4rem; }.board-scroll { padding: 1.75rem 1.15rem; }.task-modal { padding: 1.3rem; }.field-grid { grid-template-columns: 1fr; }.project-progress { gap: .35rem; } }
</style>
