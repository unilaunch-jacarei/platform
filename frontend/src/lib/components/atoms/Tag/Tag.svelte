<script lang="ts">
  import type { Snippet } from "svelte";

  type TagVariant = "default" | "accent" | "success" | "warning" | "danger";

  type TagProps = {
    variant?: TagVariant;
    children: Snippet;
    class?: string;
  };

  let {
    variant = "default",
    children,
    class: className = "",
  }: TagProps = $props();

  const variantClasses: Record<TagVariant, string> = {
    default: "bg-muted/15 text-muted-foreground border-border",
    accent: "bg-accent/15 text-accent border-accent/30",
    success: "bg-green/15 text-green border-green/30",
    warning: "bg-yellow/15 text-yellow border-yellow/30",
    danger: "bg-destructive/15 text-destructive border-destructive/30",
  };
</script>

<span
  class="inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold leading-none {variantClasses[
    variant
  ]} {className}"
>
  {@render children()}
</span>