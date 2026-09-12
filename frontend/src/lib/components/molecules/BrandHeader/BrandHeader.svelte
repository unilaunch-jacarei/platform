<script lang="ts">
  import BrandIcon from "$lib/components/atoms/BrandIcon/BrandIcon.svelte";
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";

  type BrandHeaderProps = {
    title?: string;
    subtitle?: string;
    class?: string;
  };

  let { title, subtitle, class: className = "" }: BrandHeaderProps = $props();
</script>

<div class="flex flex-col items-center text-center mb-8 gap-1.5 {className}">
  <BrandIcon size="md" class="mb-2" />

  {#if title}
    <Typography
      variant="h2"
      class="text-3xl font-bold tracking-tight text-foreground"
    >
      {title}
    </Typography>
  {/if}

  {#if subtitle}
    <Typography variant="caption" class="text-sm text-muted-foreground">
      {subtitle}
    </Typography>
  {/if}
</div>
