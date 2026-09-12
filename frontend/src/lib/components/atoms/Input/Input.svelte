<script lang="ts">
  import type { HTMLInputAttributes } from "svelte/elements";

  type InputProps = HTMLInputAttributes & {
    class?: string;
    value?: string | number | null;
  };

  let {
    class: className = "",
    type = "text",
    value = $bindable(""),
    ...restProps
  }: InputProps = $props();
</script>

<input
  {type}
  bind:value
  data-slot="input"
  class="flex h-9 w-full min-w-0 rounded-md border border-border bg-input-background px-3 py-1 text-sm text-foreground placeholder:text-muted-foreground outline-none transition-all duration-150 ease-out selection:bg-primary selection:text-primary-foreground focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 aria-invalid:ring-2 file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground file:cursor-pointer {className}"
  {...restProps}
/>
