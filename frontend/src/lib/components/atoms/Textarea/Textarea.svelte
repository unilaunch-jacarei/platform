<script lang="ts">
  import type { HTMLTextareaAttributes } from "svelte/elements";

  type TextareaProps = HTMLTextareaAttributes & {
    class?: string;
    value?: string;
  };

  let {
    class: className = "",
    value = $bindable(""),
    ...restProps
  }: TextareaProps = $props();
</script>

<textarea
  bind:value
  class="min-h-24 w-full resize-y rounded-md border border-border bg-input-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none transition-all focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring {className}"
  {...restProps}
></textarea>