<script lang="ts">
  import type { Snippet } from "svelte";

  type CenteredLayoutProps = {
    children: Snippet;
    showBrandHeader?: boolean;
    class?: string;
  };

  let {
    children,
    showBrandHeader = true,
    class: className = "",
  }: CenteredLayoutProps = $props();
</script>

<main
  class="min-h-screen w-full flex flex-col items-center justify-center p-4 bg-background relative overflow-hidden {className}"
>
  {@render children()}
</main>
