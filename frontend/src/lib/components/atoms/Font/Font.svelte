<script lang="ts">
  import type { Snippet } from "svelte";

  type FontFamily = "display" | "body" | "mono";
  type FontWeight = "normal" | "medium" | "semibold" | "bold";

  type FontProps = {
    family?: FontFamily;
    weight?: FontWeight;
    children: Snippet;
    class?: string;
  };

  let {
    family = "body",
    weight = "normal",
    children,
    class: className = "",
  }: FontProps = $props();

  const familyClasses: Record<FontFamily, string> = {
    display: "font-display",
    body: "font-body",
    mono: "font-mono",
  };

  const weightClasses: Record<FontWeight, string> = {
    normal: "font-normal",
    medium: "font-medium",
    semibold: "font-semibold",
    bold: "font-bold",
  };
</script>

<span class="{familyClasses[family]} {weightClasses[weight]} {className}">
  {@render children()}
</span>