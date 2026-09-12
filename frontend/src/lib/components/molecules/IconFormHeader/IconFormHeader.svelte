<script lang="ts">
  import type { Snippet } from "svelte";
  import IconContainer from "$lib/components/atoms/IconContainer/IconContainer.svelte";
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";

  type IconFormHeaderProps = {
    title: string;
    description: string;
    icon: Snippet;
    class?: string;
  };

  let {
    title,
    description,
    icon,
    class: className = "",
  }: IconFormHeaderProps = $props();
</script>

<div class="flex flex-col gap-3 {className}">
  <IconContainer>
    {@render icon()}
  </IconContainer>

  <div class="space-y-1">
    <Typography
      variant="h2"
      class="text-2xl font-bold tracking-tight text-white"
    >
      {title}
    </Typography>
    <Typography
      variant="caption"
      class="text-sm text-muted-foreground block leading-relaxed"
    >
      {description}
    </Typography>
  </div>
</div>
