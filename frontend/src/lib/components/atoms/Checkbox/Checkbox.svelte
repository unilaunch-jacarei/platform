<script lang="ts">
  import type { Snippet } from "svelte";
  import type { HTMLInputAttributes } from "svelte/elements";

  type CheckboxProps = Omit<HTMLInputAttributes, "type"> & {
    checked?: boolean;
    class?: string;
    children?: Snippet;
  };

  let {
    checked = $bindable(false),
    class: className = "",
    disabled = false,
    id,
    children,
    ...restProps
  }: CheckboxProps = $props();
</script>

<label
  class="inline-flex items-center gap-2.5 select-none cursor-pointer group has-[:disabled]:cursor-not-allowed has-[:disabled]:opacity-50 {className}"
>
  <span class="relative inline-flex items-center justify-center shrink-0">
    <input
      type="checkbox"
      bind:checked
      {disabled}
      {id}
      class="peer sr-only"
      {...restProps}
    />

    <span
      aria-hidden="true"
      class="size-4 rounded-xs border border-border bg-input-background transition-all duration-150 ease-out flex items-center justify-center text-primary-foreground
             peer-focus-visible:ring-2 peer-focus-visible:ring-ring peer-focus-visible:ring-offset-2 peer-focus-visible:border-primary
             peer-checked:bg-primary peer-checked:border-primary
             peer-checked:[&>svg]:opacity-100 peer-checked:[&>svg]:scale-100
             peer-aria-invalid:border-destructive
             group-hover:border-accent"
    >
      <svg
        class="size-3.5 stroke-[3] transition-all duration-150 ease-out opacity-0 scale-50 pointer-events-none"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline points="20 6 9 17 4 12" />
      </svg>
    </span>
  </span>

  {#if children}
    <span class="text-sm font-medium text-foreground">
      {@render children()}
    </span>
  {/if}
</label>
