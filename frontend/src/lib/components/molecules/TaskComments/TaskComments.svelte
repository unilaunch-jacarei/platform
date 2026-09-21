<script lang="ts">
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";
  import Icon from "$lib/components/atoms/Icon/Icon.svelte";
  import Button from "$lib/components/atoms/Button/Button.svelte";
  import Textarea from "$lib/components/atoms/Textarea/Textarea.svelte";

  type Comment = { author: string; text: string; date: string };
  type TaskCommentsProps = { comments?: Comment[] };

  let { comments = [] }: TaskCommentsProps = $props();
  let message = $state("");

  function addComment() {
    const text = message.trim();
    if (!text) return;
    comments = [...comments, { author: "Você", text, date: "agora" }];
    message = "";
  }
</script>

<section class="space-y-4">
  <div class="flex items-center justify-between">
    <Typography variant="label">Comentários</Typography>
    <Typography variant="caption">{comments.length}</Typography>
  </div>

  <div class="space-y-3">
    {#each comments as comment}
      <article class="rounded-lg border border-border bg-surface-soft/40 p-3">
        <div class="mb-1 flex items-center justify-between gap-3">
          <Typography variant="label" class="text-sm">{comment.author}</Typography>
          <Typography variant="caption" class="text-xs">{comment.date}</Typography>
        </div>
        <Typography variant="caption" class="block text-foreground">{comment.text}</Typography>
      </article>
    {:else}
      <Typography variant="caption">Ainda não há comentários nesta task.</Typography>
    {/each}
  </div>

  <form class="space-y-2 border-t border-border pt-4" onsubmit={(event) => { event.preventDefault(); addComment(); }}>
    <Textarea bind:value={message} placeholder="Escreva uma atualização ou comentário..." aria-label="Novo comentário" />
    <Button type="submit" size="sm" disabled={!message.trim()}>
      <Icon name="plus" size="sm" />
      Adicionar comentário
    </Button>
  </form>
</section>