<script lang="ts">
  import BrandHeader from "$lib/components/molecules/BrandHeader/BrandHeader.svelte";

  type BrandLogoSectionProps = {
    title?: string;
    subtitle?: string;
    class?: string;
  };

  let {
    title = "Unilaunch",
    subtitle,
    class: className = "",
  }: BrandLogoSectionProps = $props();
</script>

<section class="flex w-full flex-col items-center justify-center {className}">
  <BrandHeader {title} {subtitle} />
</section>
