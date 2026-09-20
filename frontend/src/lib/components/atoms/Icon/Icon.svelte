<script lang="ts">
  type IconName = "check" | "close" | "mail" | "plus" | "search" | "spark";

  type IconProps = {
    name: IconName;
    size?: "sm" | "md" | "lg";
    class?: string;
    label?: string;
  };

  let {
    name,
    size = "md",
    class: className = "",
    label,
  }: IconProps = $props();

  const sizeClasses = {
    sm: "size-4",
    md: "size-5",
    lg: "size-6",
  };
</script>

<svg
  class="{sizeClasses[size]} {className}"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  role={label ? "img" : undefined}
  aria-label={label}
  aria-hidden={label ? undefined : "true"}
>
  {#if name === "check"}
    <path d="m5 12 4 4L19 6" />
  {:else if name === "close"}
    <path d="M6 6l12 12M18 6 6 18" />
  {:else if name === "mail"}
    <rect x="3" y="5" width="18" height="14" rx="2" />
    <path d="m3 7 9 6 9-6" />
  {:else if name === "plus"}
    <path d="M12 5v14M5 12h14" />
  {:else if name === "search"}
    <circle cx="11" cy="11" r="7" />
    <path d="m20 20-4-4" />
  {:else}
    <path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3Z" />
    <path d="m19 16 .7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16Z" />
  {/if}
</svg>