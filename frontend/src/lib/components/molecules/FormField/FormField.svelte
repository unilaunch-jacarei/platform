<script lang="ts">
  import type { Snippet } from "svelte";
  import type { HTMLInputAttributes } from "svelte/elements";
  import Input from "../../atoms/Input/Input.svelte";
  import Typography from "../../atoms/Typography/Typography.svelte";

  type FormFieldProps = Omit<HTMLInputAttributes, "children"> & {
    id?: string;
    label?: string;
    error?: string;
    description?: string;
    required?: boolean;
    class?: string;
    value?: string | number | null;
    children?: Snippet;
  };

  let {
    id,
    label,
    error,
    description,
    required = false,
    class: className = "",
    value = $bindable(""),
    children,
    type = "text",
    ...restProps
  }: FormFieldProps = $props();
</script>

<div class="flex flex-col gap-1.5 w-full {className}">
  {#if label}
    <label for={id} class="inline-flex items-center gap-1 cursor-pointer w-fit">
      <Typography variant="label">{label}</Typography>
      {#if required}
        <span
          class="text-destructive font-bold text-xs"
          title="Campo obrigatório">*</span
        >
      {/if}
    </label>
  {/if}

  <div class="relative w-full">
    {#if children}
      {@render children()}
    {:else}
      <Input
        {id}
        {type}
        bind:value
        {required}
        aria-invalid={!!error}
        {...restProps}
      />
    {/if}
  </div>

  {#if description && !error}
    <Typography variant="caption" class="text-xs text-muted">
      {description}
    </Typography>
  {/if}

  {#if error}
    <Typography
      variant="caption"
      class="text-xs text-destructive flex items-center gap-1 font-medium transition-all duration-150"
    >
      <svg
        class="size-3.5 shrink-0 stroke-[2.5]"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12" y2="17" />
      </svg>
      {error}
    </Typography>
  {/if}
</div>
