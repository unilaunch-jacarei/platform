<!-- src/lib/components/molecules/FormButton/FormButton.svelte -->
<script lang="ts">
  import Button from "$lib/components/atoms/Button/Button.svelte";
  import type { Snippet } from "svelte";

  type FormButtonProps = {
    submitting?: boolean;
    loadingText?: string;
    children?: Snippet;
    type?: "submit" | "button" | "reset";
    class?: string;
    disabled?: boolean;
  };

  let {
    submitting = false,
    loadingText = "Carregando...",
    children,
    type = "submit",
    class: className = "",
    disabled = false,
  }: FormButtonProps = $props();
</script>

<Button
  {type}
  size="lg"
  class="w-full mt-2 {className}"
  disabled={submitting || disabled}
>
  {#if submitting}
    {loadingText}
  {:else if children}
    {@render children()}
  {/if}
</Button>
