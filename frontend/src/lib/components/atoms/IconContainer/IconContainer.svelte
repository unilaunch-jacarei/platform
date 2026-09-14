<script lang="ts">
  import type { Snippet } from "svelte";

  type IconContainerProps = {
    children: Snippet;
    class?: string;
  };

  let { children, class: className = "" }: IconContainerProps = $props();
</script>

<div
  class="size-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary {className}"
>
  {@render children()}
</div>
