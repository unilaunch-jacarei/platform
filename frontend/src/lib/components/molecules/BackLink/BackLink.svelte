<!-- src/lib/components/molecules/BackLink/BackLink.svelte -->
<script lang="ts">
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";

  type BackLinkProps = {
    href: string;
    label: string;
    class?: string;
  };

  let { href, label, class: className = "" }: BackLinkProps = $props();
</script>

<Typography
  variant="link"
  {href}
  class="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground no-underline transition-colors w-fit {className}"
>
  <svg
    class="size-4"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <line x1="19" y1="12" x2="5" y2="12" />
    <polyline points="12 19 5 12 12 5" />
  </svg>
  <span>{label}</span>
</Typography>
