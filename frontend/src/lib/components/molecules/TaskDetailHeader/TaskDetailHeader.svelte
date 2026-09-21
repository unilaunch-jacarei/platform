<script lang="ts">
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";
  import Tag from "$lib/components/atoms/Tag/Tag.svelte";
  import Icon from "$lib/components/atoms/Icon/Icon.svelte";
  import Button from "$lib/components/atoms/Button/Button.svelte";

  type TaskDetailHeaderProps = {
    title: string;
    description?: string;
    statusLabel?: string;
    onClose: () => void;
  };

  let { title, description, statusLabel, onClose }: TaskDetailHeaderProps = $props();
</script>

<header class="flex items-start justify-between gap-4 border-b border-border pb-5">
  <div class="min-w-0 space-y-3">
    {#if statusLabel}<Tag variant="accent">{statusLabel}</Tag>{/if}
    <Typography variant="h2">{title}</Typography>
    {#if description}<Typography variant="caption">{description}</Typography>{/if}
  </div>
  <Button variant="ghost" size="icon" aria-label="Fechar detalhes da task" onclick={onClose}>
    <Icon name="close" />
  </Button>
</header>