<script lang="ts">
	import Typography from "$lib/components/atoms/Typography/Typography.svelte";
	import Icon from "$lib/components/atoms/Icon/Icon.svelte";
	import KanbanColumn from "$lib/components/molecules/KanbanColumn/KanbanColumn.svelte";

	type Project = {
		title: string;
		description: string;
		tags: { label: string; variant?: "default" | "accent" | "success" | "warning" | "danger" }[];
		status?: "default" | "accent" | "success" | "warning" | "danger";
		statusLabel: string;
		metadata: string;
		progress: number;
	};

	type Column = {
		title: string;
		description: string;
		accent: "muted" | "accent" | "warning" | "success";
		projects: Project[];
	};

	let columns = $state<Column[]>([
		{
			title: "Backlog",
			description: "Ideias e próximos passos",
			accent: "muted" as const,
			projects: [
				{ title: "Setup CI/CD pipeline", description: "Automatizar testes e publicação dos serviços.", tags: [{ label: "DevOps", variant: "accent" as const }], statusLabel: "Baixa", metadata: "20/07", progress: 12 },
				{ title: "Documentação da API", description: "Registrar endpoints e exemplos de integração.", tags: [{ label: "Documentação", variant: "default" as const }, { label: "API", variant: "accent" as const }], status: "warning" as const, statusLabel: "Média", metadata: "25/07", progress: 28 },
			],
		},
		{
			title: "A fazer",
			description: "Prontos para começar",
			accent: "accent" as const,
			projects: [
				{ title: "Tela de dashboard v2", description: "Evoluir a visão de métricas do produto.", tags: [{ label: "Front-end", variant: "accent" as const }, { label: "UI", variant: "success" as const }], status: "danger" as const, statusLabel: "Alta", metadata: "18/07", progress: 42 },
				{ title: "Integração Stripe", description: "Adicionar pagamentos recorrentes aos planos.", tags: [{ label: "Back-end", variant: "success" as const }, { label: "API", variant: "accent" as const }], status: "danger" as const, statusLabel: "Alta", metadata: "19/07", progress: 35 },
			],
		},
		{
			title: "Em andamento",
			description: "Trabalho em execução",
			accent: "accent" as const,
			projects: [
				{ title: "Refatorar autenticação", description: "Simplificar sessões e recuperação de acesso.", tags: [{ label: "Auth", variant: "warning" as const }, { label: "Back-end", variant: "success" as const }], status: "danger" as const, statusLabel: "Alta", metadata: "15/07", progress: 68 },
				{ title: "Testes unitários", description: "Cobrir os fluxos críticos do produto.", tags: [{ label: "QA", variant: "warning" as const }], status: "warning" as const, statusLabel: "Média", metadata: "16/07", progress: 54 },
			],
		},
		{
			title: "Em revisão",
			description: "Aguardando validação",
			accent: "warning" as const,
			projects: [
				{ title: "Busca com filtros", description: "Validar filtros e ordenação com o time.", tags: [{ label: "Front-end", variant: "accent" as const }, { label: "UI", variant: "success" as const }], status: "warning" as const, statusLabel: "Média", metadata: "12/07", progress: 86 },
			],
		},
		{
			title: "Concluído",
			description: "Entregas finalizadas",
			accent: "success" as const,
			projects: [
				{ title: "Setup do projeto", description: "Estrutura inicial pronta para o time.", tags: [{ label: "DevOps", variant: "accent" as const }], status: "danger" as const, statusLabel: "Alta", metadata: "01/07", progress: 100 },
			],
		},
	]);

	function moveProject(projectTitle: string, targetColumnTitle: string) {
		let movedProject: Project | undefined;

		columns = columns.map((column) => {
			const project = column.projects.find((item) => item.title === projectTitle);
			if (project) movedProject = project;
			return project
				? { ...column, projects: column.projects.filter((item) => item.title !== projectTitle) }
				: column;
		});

		if (!movedProject) return;

		columns = columns.map((column) =>
			column.title === targetColumnTitle
				? { ...column, projects: [...column.projects, movedProject!] }
				: column
		);
	}
</script>

<svelte:head>
	<title>Kanban | UniLaunch</title>
</svelte:head>

<main class="min-h-[calc(100vh-4rem)] bg-background px-5 py-8 text-foreground sm:px-8 lg:px-10">
	<div class="mx-auto max-w-[1600px]">
		<header class="mb-8 flex flex-col justify-between gap-5 border-b border-border/70 pb-6 sm:flex-row sm:items-end">
			<div>
				<Typography variant="kicker">Workspace / Projetos</Typography>
				<Typography variant="h1" class="mt-2">Kanban de projetos</Typography>
				<Typography variant="caption" class="mt-3 block max-w-xl">Acompanhe o trabalho do UniLaunch e mova cada projeto pela etapa certa.</Typography>
			</div>
			<div class="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm text-muted-foreground">
				<Icon name="spark" size="sm" class="text-accent" />
				<span>8 projetos no quadro</span>
			</div>
		</header>

		<div class="flex gap-4 overflow-x-auto pb-4">
			{#each columns as column}
				<KanbanColumn {...column} onMoveProject={(projectTitle) => moveProject(projectTitle, column.title)} />
			{/each}
		</div>
	</div>
</main>
