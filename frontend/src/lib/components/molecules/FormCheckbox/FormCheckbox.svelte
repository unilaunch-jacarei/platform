<script lang="ts">
  import type { Snippet } from "svelte";
  import Checkbox from "../../atoms/Checkbox/Checkbox.svelte";
  import Typography from "../../atoms/Typography/Typography.svelte";

  type FormCheckboxProps = {
    id: string;
    name?: string;
    label?: string;
    children?: Snippet;
    checked?: boolean;
    required?: boolean;
    disabled?: boolean;
    class?: string;
  };

  let {
    id,
    name,
    label,
    children,
    checked = $bindable(false),
    required = false,
    disabled = false,
    class: className = "",
  }: FormCheckboxProps = $props();
</script>

<div class="flex items-center gap-2 pt-1 {className}">
  <Checkbox {id} {name} bind:checked {disabled} {required}>
    {#if children}
      {@render children()}
    {:else}
      <Typography
        variant="caption"
        class="text-xs text-muted cursor-pointer select-none"
      >
        {label}
      </Typography>
    {/if}
  </Checkbox>
</div>
