<script lang="ts">
  import type { Snippet } from "svelte";
  import type { HTMLAttributes } from "svelte/elements";

  type TypographyVariant =
    | "h1"
    | "h2"
    | "body"
    | "caption"
    | "kicker"
    | "label"
    | "link"
    | "form-footer"
    | "subtitle";

  type TypographyProps = HTMLAttributes<HTMLElement> & {
    variant?: TypographyVariant;
    children: Snippet;
    class?: string;
    href?: string;
  };

  let {
    variant = "body",
    children,
    class: className = "",
    ...restProps
  }: TypographyProps = $props();

  const elements: Record<TypographyVariant, string> = {
    h1: "h1",
    h2: "h2",
    body: "p",
    caption: "span",
    kicker: "p",
    label: "span",
    link: "a",
    "form-footer": "p",
    subtitle: "h2",
  };

  const variants: Record<TypographyVariant, string> = {
    h1: "text-[clamp(2rem,4vw,3.3rem)] font-bold text-foreground leading-none tracking-[-0.04em]",
    h2: "text-[clamp(1.7rem,3vw,2.2rem)] font-bold text-foreground leading-[1.2] tracking-[-0.04em]",

    body: "text-base text-foreground leading-[1.7]",

    kicker:
      "mb-2.5 text-[0.82rem] font-bold uppercase tracking-[0.18em] text-accent",
    caption: "text-[0.92rem] text-muted leading-normal",
    label: "text-[0.92rem] font-semibold text-foreground",
    link: "mt-3 inline-block font-semibold text-accent no-underline hover:underline cursor-pointer transition-colors duration-150",
    "form-footer": "mt-4.5 text-center text-sm text-muted",
    subtitle: "mb-1.5 text-base font-semibold text-foreground leading-[1.4]",
  };

  const element = $derived(elements[variant]);
  const variantClass = $derived(variants[variant]);
</script>

<svelte:element
  this={element}
  class="{variantClass} {className}"
  {...restProps}
>
  {@render children()}
</svelte:element>
