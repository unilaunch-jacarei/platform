<script lang="ts">
  import Icon from "$lib/components/atoms/Icon/Icon.svelte";
  import TaskDetailHeader from "$lib/components/molecules/TaskDetailHeader/TaskDetailHeader.svelte";
  import TaskChecklist from "$lib/components/molecules/TaskChecklist/TaskChecklist.svelte";
  import TaskComments from "$lib/components/molecules/TaskComments/TaskComments.svelte";

  type TaskModalProps = {
    title: string;
    description?: string;
    statusLabel?: string;
    metadata?: string;
    progress?: number;
    checklist?: { label: string; completed: boolean }[];
    comments?: { author: string; text: string; date: string }[];
    onClose: () => void;
  };

  let { title, description, statusLabel, metadata, progress, checklist = [], comments = [], onClose }: TaskModalProps = $props();

  function handleBackdrop(event: MouseEvent) {
    if (event.target === event.currentTarget) onClose();
  }
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm" role="presentation" onclick={handleBackdrop}>
  <div class="max-h-[min(760px,calc(100vh-2rem))] w-full max-w-2xl overflow-y-auto rounded-2xl border border-border bg-card p-6 shadow-2xl" role="dialog" aria-modal="true" aria-labelledby="task-modal-title">
    <div id="task-modal-title">
      <TaskDetailHeader {title} {description} {statusLabel} {onClose} />
    </div>

    <div class="grid gap-6 py-5 sm:grid-cols-3">
      <div class="rounded-lg border border-border bg-surface-soft/40 p-3">
        <span class="block text-xs text-muted-foreground">Prazo</span>
        <span class="text-sm font-semibold text-foreground">{metadata ?? "Sem prazo"}</span>
      </div>
      <div class="rounded-lg border border-border bg-surface-soft/40 p-3">
        <span class="block text-xs text-muted-foreground">Progresso</span>
        <span class="text-sm font-semibold text-foreground">{progress ?? 0}%</span>
      </div>
      <div class="rounded-lg border border-border bg-surface-soft/40 p-3">
        <span class="block text-xs text-muted-foreground">Ações</span>
        <span class="flex items-center gap-1 text-sm font-semibold text-accent"><Icon name="spark" size="sm" /> Em acompanhamento</span>
      </div>
    </div>

    <div class="space-y-6">
      <TaskChecklist items={checklist} />
      <TaskComments comments={comments} />
    </div>
  </div>
</div>