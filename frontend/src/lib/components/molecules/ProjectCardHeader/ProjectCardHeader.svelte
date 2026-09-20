<script lang="ts">
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";
  import Tag from "$lib/components/atoms/Tag/Tag.svelte";

  type Status = "default" | "accent" | "success" | "warning" | "danger";

  type ProjectCardHeaderProps = {
    title: string;
    description?: string;
    status?: Status;
    statusLabel?: string;
  };

  let { title, description, status = "default", statusLabel }: ProjectCardHeaderProps = $props();
</script>

<header class="flex items-start justify-between gap-4">
  <div class="min-w-0 space-y-1">
    <Typography variant="subtitle" class="truncate">{title}</Typography>
    {#if description}
      <Typography variant="caption" class="line-clamp-2">{description}</Typography>
    {/if}
  </div>

  {#if statusLabel}
    <Tag variant={status} class="shrink-0">{statusLabel}</Tag>
  {/if}
</header>