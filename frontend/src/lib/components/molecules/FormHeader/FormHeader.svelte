<script lang="ts">
  import Typography from "../../atoms/Typography/Typography.svelte";

  type FormHeaderProps = {
    title: string;
    description?: string;
    class?: string;
  };

  let { title, description, class: className = "" }: FormHeaderProps = $props();
</script>

<div class="flex flex-col gap-0.5 mb-5 {className}">
  <Typography variant="subtitle" class="text-lg font-bold">
    {title}
  </Typography>
  {#if description}
    <Typography variant="caption" class="text-xs text-muted">
      {description}
    </Typography>
  {/if}
</div>
