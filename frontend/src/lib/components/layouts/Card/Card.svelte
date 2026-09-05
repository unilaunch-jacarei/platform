<script lang="ts">
  import type { Snippet } from "svelte";
  import type { HTMLAttributes } from "svelte/elements";

  type CardProps = HTMLAttributes<HTMLDivElement> & {
    children: Snippet;
    class?: string;
  };

  let { children, class: className = "", ...restProps }: CardProps = $props();
</script>

<div
  class="w-full max-w-md rounded-2xl border border-border bg-card/80 p-8 shadow-2xl backdrop-blur-md transition-all duration-200 {className}"
  {...restProps}
>
  {@render children()}
</div>
