<script lang="ts">
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";
  import Checkbox from "$lib/components/atoms/Checkbox/Checkbox.svelte";

  type ChecklistItem = { label: string; completed: boolean };
  type TaskChecklistProps = { items?: ChecklistItem[] };

  let { items = [] }: TaskChecklistProps = $props();
  let completedCount = $derived(items.filter((item) => item.completed).length);
</script>

<section class="space-y-3">
  <div class="flex items-center justify-between">
    <Typography variant="label">Checklist</Typography>
    <Typography variant="caption">{completedCount}/{items.length}</Typography>
  </div>
  {#if items.length}
    <div class="space-y-3 rounded-lg border border-border bg-surface-soft/40 p-4">
      {#each items as item}
        <Checkbox bind:checked={item.completed}>
          {item.label}
        </Checkbox>
      {/each}
    </div>
  {:else}
    <Typography variant="caption">Nenhum item no checklist.</Typography>
  {/if}
</section>