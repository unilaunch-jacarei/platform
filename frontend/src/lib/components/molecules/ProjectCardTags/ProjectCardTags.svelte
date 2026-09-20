<script lang="ts">
  import Tag from "$lib/components/atoms/Tag/Tag.svelte";

  type TagItem = {
    label: string;
    variant?: "default" | "accent" | "success" | "warning" | "danger";
  };

  type ProjectCardTagsProps = {
    tags: TagItem[];
  };

  let { tags }: ProjectCardTagsProps = $props();
</script>

{#if tags.length > 0}
  <div class="flex flex-wrap gap-2">
    {#each tags as tag}
      <Tag variant={tag.variant}>{tag.label}</Tag>
    {/each}
  </div>
{/if}