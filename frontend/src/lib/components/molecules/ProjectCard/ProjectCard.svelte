<script lang="ts">
  import ProjectCardHeader from "$lib/components/molecules/ProjectCardHeader/ProjectCardHeader.svelte";
  import ProjectCardTags from "$lib/components/molecules/ProjectCardTags/ProjectCardTags.svelte";
  import ProjectCardMeta from "$lib/components/molecules/ProjectCardMeta/ProjectCardMeta.svelte";

  type ProjectTag = {
    label: string;
    variant?: "default" | "accent" | "success" | "warning" | "danger";
  };

  type ProjectCardProps = {
    title: string;
    description?: string;
    tags?: ProjectTag[];
    status?: "default" | "accent" | "success" | "warning" | "danger";
    statusLabel?: string;
    metadata?: string;
    progress?: number;
    class?: string;
    onDragStart?: (event: DragEvent) => void;
  };

  let {
    title,
    description,
    tags = [],
    status = "default",
    statusLabel,
    metadata,
    progress,
    class: className = "",
    onDragStart,
  }: ProjectCardProps = $props();
</script>

<article
  draggable="true"
  ondragstart={onDragStart}
  class="group flex w-full cursor-grab flex-col gap-4 rounded-xl border border-border bg-card p-5 transition-colors duration-200 hover:border-accent/50 active:cursor-grabbing {className}"
>
  <ProjectCardHeader {title} {description} {status} {statusLabel} />
  <ProjectCardTags {tags} />
  <ProjectCardMeta {metadata} {progress} />
</article>