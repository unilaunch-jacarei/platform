<script lang="ts">
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";
  import Icon from "$lib/components/atoms/Icon/Icon.svelte";
  import ProjectCard from "$lib/components/molecules/ProjectCard/ProjectCard.svelte";

  type Project = {
    title: string;
    description?: string;
    tags?: {
      label: string;
      variant?: "default" | "accent" | "success" | "warning" | "danger";
    }[];
    status?: "default" | "accent" | "success" | "warning" | "danger";
    statusLabel?: string;
    metadata?: string;
    progress?: number;
  };

  type KanbanColumnProps = {
    title: string;
    description: string;
    accent: "muted" | "accent" | "warning" | "success";
    projects: Project[];
    onMoveProject: (projectTitle: string) => void;
    onOpenProject: (project: Project) => void;
  };

  let { title, description, accent, projects, onMoveProject, onOpenProject }: KanbanColumnProps = $props();

  const accentClasses = {
    muted: "bg-muted-foreground",
    accent: "bg-accent",
    warning: "bg-yellow",
    success: "bg-green",
  };

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    const projectTitle = event.dataTransfer?.getData("text/plain");
    if (projectTitle) onMoveProject(projectTitle);
  }
</script>

<section
  aria-label="Fila {title}"
  class="flex min-w-[18rem] flex-1 flex-col rounded-2xl border border-border/70 bg-surface/60 p-3 transition-colors hover:border-accent/40"
  ondragover={(event) => event.preventDefault()}
  ondrop={handleDrop}
>
  <header class="mb-3 flex items-start justify-between gap-3 px-2 py-1">
    <div class="flex min-w-0 items-start gap-2.5">
      <span class="mt-1.5 size-2.5 shrink-0 rounded-full {accentClasses[accent]}"></span>
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <Typography variant="label" class="truncate">{title}</Typography>
          <span class="rounded-full bg-muted/15 px-2 py-0.5 font-mono text-xs text-muted-foreground">{projects.length}</span>
        </div>
        <Typography variant="caption" class="text-xs">{description}</Typography>
      </div>
    </div>
    <button class="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-muted/15 hover:text-foreground" aria-label="Adicionar projeto em {title}">
      <Icon name="plus" size="sm" />
    </button>
  </header>

  <div class="flex flex-1 flex-col gap-3">
    {#each projects as project}
      <ProjectCard
        {...project}
        onDragStart={(event) => event.dataTransfer?.setData("text/plain", project.title)}
        onOpen={() => onOpenProject(project)}
      />
    {:else}
      <div class="flex min-h-28 items-center justify-center rounded-xl border border-dashed border-border px-4 text-center">
        <Typography variant="caption">Nenhum projeto nesta etapa</Typography>
      </div>
    {/each}
  </div>
</section>