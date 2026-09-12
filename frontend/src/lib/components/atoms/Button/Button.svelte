<script lang="ts">
  import type { Snippet } from "svelte";
  import type {
    HTMLButtonAttributes,
    HTMLAnchorAttributes,
  } from "svelte/elements";

  type ButtonVariant =
    | "default"
    | "destructive"
    | "outline"
    | "secondary"
    | "ghost"
    | "link";
  type ButtonSize = "default" | "sm" | "lg" | "icon";

  type BaseProps = {
    variant?: ButtonVariant;
    size?: ButtonSize;
    class?: string;
    children?: Snippet;
    href?: string;
  };

  type ButtonProps = BaseProps & HTMLButtonAttributes & HTMLAnchorAttributes;

  let {
    variant = "default",
    size = "default",
    class: className = "",
    children,
    href,
    type = "button",
    ...restProps
  }: ButtonProps = $props();

  const variants: Record<ButtonVariant, string> = {
    default:
      "bg-gradient-to-r from-primary to-accent text-white shadow-[0_0_20px_rgba(124,58,237,0.35),0_6px_16px_rgba(99,102,241,0.2)] hover:shadow-[0_0_24px_rgba(124,58,237,0.45),0_8px_20px_rgba(99,102,241,0.25)] hover:brightness-110 hover:-translate-y-0.5 active:translate-y-0 active:brightness-100",
    destructive:
      "bg-destructive text-destructive-foreground hover:opacity-90 hover:-translate-y-0.5 active:translate-y-0",
    outline:
      "border border-border bg-transparent text-foreground hover:bg-surface-soft hover:-translate-y-0.5 active:translate-y-0",
    secondary:
      "bg-surface-soft text-foreground hover:bg-surface-strong hover:-translate-y-0.5 active:translate-y-0",
    ghost: "bg-transparent text-foreground hover:bg-surface-soft",
    link: "h-auto p-0 bg-transparent text-accent hover:underline",
  };

  const sizes: Record<ButtonSize, string> = {
    default: "h-10 px-4 py-2 text-sm rounded-md",
    sm: "h-8 px-3 text-xs rounded-sm",
    lg: "h-11 px-6 text-base rounded-lg",
    icon: "h-9 w-9 p-0 rounded-md shrink-0",
  };

  const baseClasses =
    "inline-flex items-center justify-center gap-2 font-semibold whitespace-nowrap transition-all duration-200 ease-out outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&>svg]:size-4 [&>svg]:shrink-0 cursor-pointer select-none";
</script>

{#if href}
  <a
    {href}
    class="{baseClasses} {variants[variant]} {sizes[size]} {className}"
    {...restProps}
  >
    {@render children?.()}
  </a>
{:else}
  <button
    {type}
    class="{baseClasses} {variants[variant]} {sizes[size]} {className}"
    {...restProps}
  >
    {@render children?.()}
  </button>
{/if}
