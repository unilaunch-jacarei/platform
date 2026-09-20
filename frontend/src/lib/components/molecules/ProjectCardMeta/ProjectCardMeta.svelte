<script lang="ts">
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";
  import Icon from "$lib/components/atoms/Icon/Icon.svelte";

  type ProjectCardMetaProps = {
    metadata?: string;
    progress?: number;
  };

  let { metadata, progress }: ProjectCardMetaProps = $props();
  const safeProgress = $derived(progress === undefined ? 0 : Math.min(100, Math.max(0, progress)));
</script>

{#if progress !== undefined || metadata}
  <footer class="mt-auto flex items-center justify-between gap-4 border-t border-border/70 pt-3">
    {#if metadata}
      <div class="flex min-w-0 items-center gap-1.5 text-muted-foreground">
        <Icon name="spark" size="sm" />
        <Typography variant="caption" class="truncate">{metadata}</Typography>
      </div>
    {/if}

    {#if progress !== undefined}
      <div class="flex shrink-0 items-center gap-2" aria-label="Progresso: {safeProgress}%">
        <div class="h-1.5 w-16 overflow-hidden rounded-full bg-muted/20">
          <div class="h-full rounded-full bg-accent" style="width: {safeProgress}%"></div>
        </div>
        <Typography variant="caption">{safeProgress}%</Typography>
      </div>
    {/if}
  </footer>
{/if}